import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUEUE_FILE = PROJECT_ROOT / "data" / "review_queue.csv"

VALID_STATUSES = {
    "approved",
    "rejected",
    "needs_research",
}


def review_queue():
    with QUEUE_FILE.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        columns = reader.fieldnames

    if not rows:
        print("The review queue is empty.")
        return

    reviewed = 0

    for book in rows:
        if book["review_status"] != "pending":
            continue

        print("\n" + "=" * 55)
        print(f"Title: {book['title']}")
        print(f"Author(s): {book['authors']}")
        print(f"Year: {book['publication_year']}")
        print(f"Subjects: {book['subjects']}")

        print("\nChoose a status:")
        print("[a] Approve")
        print("[r] Reject")
        print("[n] Needs research")
        print("[s] Skip")
        print("[q] Quit")

        choice = input("\nYour choice: ").strip().lower()

        if choice == "q":
            break
        elif choice == "s":
            continue
        elif choice == "a":
            book["review_status"] = "approved"
        elif choice == "r":
            book["review_status"] = "rejected"
        elif choice == "n":
            book["review_status"] = "needs_research"
        else:
            print("Invalid choice. Book left pending.")
            continue

        reviewed += 1

    with QUEUE_FILE.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nReview session complete. Updated: {reviewed}")


if __name__ == "__main__":
    review_queue()
