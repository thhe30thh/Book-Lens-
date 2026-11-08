import csv
from pathlib import Path

from booklens.database import get_db


REQUIRED_COLUMNS = {
    "title",
    "publication_year",
    "language",
    "authors",
}


def import_works_from_csv(csv_path):
    """Import books and their authors from a CSV file."""

    path = Path(csv_path)

    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    db = get_db()

    imported_works = 0
    imported_authors = 0
    created_connections = 0

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV file is empty or has no header.")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                f"Missing CSV columns: {', '.join(sorted(missing_columns))}"
            )

        rows = list(reader)

    prepared_rows = []

    for line_number, row in enumerate(rows, start=2):
        title = (row.get("title") or "").strip()
        language = (row.get("language") or "").strip().lower()
        authors = [
            name.strip()
            for name in (row.get("authors") or "").split(";")
            if name.strip()
        ]

        year_text = (row.get("publication_year") or "").strip()

        if not title or not language or not authors:
            raise ValueError(
                f"Line {line_number}: title, language, and authors are required."
            )

        try:
            year = int(year_text) if year_text else None
        except ValueError:
            raise ValueError(
                f"Line {line_number}: invalid publication year."
            )

        if year is not None and not 0 <= year <= 2100:
            raise ValueError(
                f"Line {line_number}: publication year is out of range."
            )

        prepared_rows.append({
            "title": title,
            "year": year,
            "language": language,
            "authors": authors,
            "original_title": (row.get("original_title") or "").strip() or None,
            "description": (row.get("description") or "").strip() or None,
        })

    with db:
        for row in prepared_rows:
            work = db.execute(
                """
                SELECT id FROM works
                WHERE title = ?
                AND publication_year IS ?
                AND language = ?
                """,
                (row["title"], row["year"], row["language"])
            ).fetchone()

            if work is None:
                cursor = db.execute(
                    """
                    INSERT INTO works (
                        title,
                        original_title,
                        publication_year,
                        language,
                        description
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        row["title"],
                        row["original_title"],
                        row["year"],
                        row["language"],
                        row["description"],
                    )
                )
                work_id = cursor.lastrowid
                imported_works += 1
            else:
                work_id = work["id"]

            for author_name in row["authors"]:
                author = db.execute(
                    "SELECT id FROM authors WHERE name = ?",
                    (author_name,)
                ).fetchone()

                if author is None:
                    cursor = db.execute(
                        "INSERT INTO authors (name) VALUES (?)",
                        (author_name,)
                    )
                    author_id = cursor.lastrowid
                    imported_authors += 1
                else:
                    author_id = author["id"]

                result = db.execute(
                    """
                    INSERT OR IGNORE INTO work_authors (
                        work_id,
                        author_id,
                        role
                    )
                    VALUES (?, ?, 'author')
                    """,
                    (work_id, author_id)
                )

                if result.rowcount > 0:
                    created_connections += 1

    return {
        "works_imported": imported_works,
        "authors_imported": imported_authors,
        "connections_created": created_connections,
    }
