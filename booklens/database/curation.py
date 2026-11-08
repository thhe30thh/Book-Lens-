import csv
from pathlib import Path


def normalize_search_results(data):
    """Convert Open Library results into reviewable book candidates."""

    candidates = []
    seen = set()

    for book in data.get("docs", []):
        title = (book.get("title") or "").strip()
        authors = book.get("author_name") or []
        work_id = book.get("key")

        if book.get("type") != "work":
            continue

        if not title or not authors or not work_id:
            continue

        if work_id in seen:
            continue

        seen.add(work_id)

        candidates.append({
            "openlibrary_id": work_id,
            "title": title,
            "authors": authors,
            "publication_year": book.get("first_publish_year"),
            "edition_count": book.get("edition_count", 0),
            "subjects": (book.get("subject") or [])[:15],
            "edition_languages": book.get("language") or [],
            "review_status": "pending",
        })

    return candidates


def export_review_queue(candidates, output_path):
    """Export book candidates into a CSV file for manual review."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    columns = [
        "openlibrary_id",
        "title",
        "authors",
        "publication_year",
        "edition_count",
        "subjects",
        "edition_languages",
        "review_status",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()

        for candidate in candidates:
            row = candidate.copy()
            row["authors"] = "; ".join(row["authors"])
            row["subjects"] = "; ".join(row["subjects"])
            row["edition_languages"] = "; ".join(
                row["edition_languages"]
            )
            writer.writerow(row)

    return len(candidates)
