import csv
import re
from pathlib import Path
from urllib.parse import urlparse

from booklens.database import get_db


REQUIRED_COLUMNS = {
    "verified_title",
    "verified_author",
    "verified_publication_year",
    "source_url",
    "review_status",
    "verification_status",
    "date_basis",
    "metadata_note",
}


def clean_source_url(value):
    """Extract and validate a plain HTTP(S) URL."""
    value = (value or "").strip()

    match = re.fullmatch(r"\[(https?://[^\]]+)\]\((https?://[^\)]+)\)", value)

    if match:
        if match.group(1) != match.group(2):
            raise ValueError("Markdown link text and destination differ.")
        value = match.group(1)

    parsed = urlparse(value)

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Invalid source URL.")

    return value


def read_verified_works(csv_path):
    """Read and validate approved, verified book records."""
    path = Path(csv_path)

    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV file is empty or has no header.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing:
            raise ValueError(
                f"Missing CSV columns: {', '.join(sorted(missing))}"
            )

        prepared = []

        for line_number, row in enumerate(reader, start=2):
            if (
                (row.get("review_status") or "").strip().lower() != "approved"
                or (row.get("verification_status") or "").strip().lower() != "verified"
            ):
                raise ValueError(
                    f"Line {line_number}: record is not approved and verified."
                )

            title = (row.get("verified_title") or "").strip()
            author = (row.get("verified_author") or "").strip()
            year_text = (row.get("verified_publication_year") or "").strip()

            if not title or not author or not year_text:
                raise ValueError(
                    f"Line {line_number}: verified title, author, and year are required."
                )

            try:
                year = int(year_text)
            except ValueError:
                raise ValueError(
                    f"Line {line_number}: invalid verified publication year."
                )

            if not 0 <= year <= 2100:
                raise ValueError(
                    f"Line {line_number}: publication year is out of range."
                )

            try:
                source_url = clean_source_url(row.get("source_url"))
            except ValueError as error:
                raise ValueError(f"Line {line_number}: {error}") from error

            prepared.append({
                "title": title,
                "author": author,
                "year": year,
                "source_url": source_url,
                "date_basis": (row.get("date_basis") or "").strip(),
                "metadata_note": (row.get("metadata_note") or "").strip(),
            })

    if not prepared:
        raise ValueError("No verified records found.")

    titles = [row["title"].casefold() for row in prepared]

    if len(titles) != len(set(titles)):
        raise ValueError("CSV contains duplicate verified titles.")

    return prepared


def preview_verified_import(csv_path):
    """Validate the CSV and return a summary without changing the database."""
    records = read_verified_works(csv_path)

    return {
        "records_found": len(records),
        "titles": [row["title"] for row in records],
        "authors": len({row["author"] for row in records}),
        "sources": len({row["source_url"] for row in records}),
        "special_date_notes": [
            row["title"]
            for row in records
            if row["date_basis"] != "first_publication"
            or row["metadata_note"]
        ],
    }


def import_verified_works(csv_path):
    """Import approved works, authors, and their supporting sources."""
    records = read_verified_works(csv_path)
    db = get_db()

    works_imported = 0
    authors_imported = 0
    connections_created = 0
    sources_created = 0
    source_connections_created = 0

    with db:
        for row in records:
            work = db.execute(
                """
                SELECT id FROM works
                WHERE title = ?
                AND publication_year = ?
                """,
                (row["title"], row["year"])
            ).fetchone()

            if work is None:
                cursor = db.execute(
                    """
                    INSERT INTO works (title, publication_year)
                    VALUES (?, ?)
                    """,
                    (row["title"], row["year"])
                )
                work_id = cursor.lastrowid
                works_imported += 1
            else:
                work_id = work["id"]

            author = db.execute(
                "SELECT id FROM authors WHERE name = ?",
                (row["author"],)
            ).fetchone()

            if author is None:
                cursor = db.execute(
                    "INSERT INTO authors (name) VALUES (?)",
                    (row["author"],)
                )
                author_id = cursor.lastrowid
                authors_imported += 1
            else:
                author_id = author["id"]

            result = db.execute(
                """
                INSERT OR IGNORE INTO work_authors (
                    work_id, author_id, role
                )
                VALUES (?, ?, 'author')
                """,
                (work_id, author_id)
            )

            if result.rowcount > 0:
                connections_created += 1

            source = db.execute(
                "SELECT id FROM sources WHERE url = ?",
                (row["source_url"],)
            ).fetchone()

            source_notes = (
                f"Date basis: {row['date_basis']}"
                + (
                    f"\nMetadata note: {row['metadata_note']}"
                    if row["metadata_note"]
                    else ""
                )
            )

            if source is None:
                cursor = db.execute(
                    """
                    INSERT INTO sources (title, url, source_type, notes)
                    VALUES (?, ?, 'bibliographic', ?)
                    """,
                    (row["title"], row["source_url"], source_notes)
                )
                source_id = cursor.lastrowid
                sources_created += 1
            else:
                source_id = source["id"]

            result = db.execute(
                """
                INSERT OR IGNORE INTO work_sources (work_id, source_id)
                VALUES (?, ?)
                """,
                (work_id, source_id)
            )

            if result.rowcount > 0:
                source_connections_created += 1

    return {
        "works_imported": works_imported,
        "authors_imported": authors_imported,
        "author_connections_created": connections_created,
        "sources_created": sources_created,
        "source_connections_created": source_connections_created,
    }
