from pathlib import Path

from booklens.database.openlibrary import search_works
from booklens.database.curation import (
    normalize_search_results,
    export_review_queue,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_FILE = PROJECT_ROOT / "data" / "review_queue.csv"

SEARCH_QUERIES = [
    "subject:literary fiction",
    "subject:world literature",
    "subject:modern fiction",
]


def main():
    all_candidates = []
    seen_ids = set()

    for query in SEARCH_QUERIES:
        print(f"\nSearching: {query}")

        try:
            results = search_works(query, limit=20)
            candidates = normalize_search_results(results)

        except Exception as error:
            print(f"Search failed: {error}")
            continue

        new_count = 0

        for candidate in candidates:
            work_id = candidate["openlibrary_id"]

            if work_id not in seen_ids:
                seen_ids.add(work_id)
                all_candidates.append(candidate)
                new_count += 1

        print(f"New candidates found: {new_count}")

    exported = export_review_queue(
        all_candidates,
        OUTPUT_FILE
    )

    print("\nCollection complete.")
    print(f"Total unique candidates: {exported}")
    print(f"Review queue saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
