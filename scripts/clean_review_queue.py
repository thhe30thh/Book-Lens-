import csv
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "review_queue.csv"

REJECT = {
    "married by arrangement",
    "the cozakis bride",
    "sleeping with a stranger",
    "marriage on the rebound",
    "his wedding-night heir",
    "the italian's stolen bride",
    "naive bride, defiant wife",
    "to make a marriage",
    "the italian's inexperienced mistress",
    "one night...nine-month scandal",
    "the banker's convenient wife",
    "master of pleasure",
    "the bellini bride",
    "ruthless magnate, convenient wife",
    "the boss's virgin",
    "the sheikh's secret babies",
    "claiming his christmas bride",
    "a little history of the world",
    "the silk roads",
    "world war ii (dk eyewitness books)",
    "a child's history of the world",
    "marvel masterworks",
    "fingersmith",
}

RESEARCH = {
    "going solo",
    "wrecking ball",
}

with QUEUE.open("r", encoding="utf-8", newline="") as file:
    reader = csv.DictReader(file)
    rows = list(reader)
    columns = reader.fieldnames

if not columns or not rows:
    raise SystemExit("Review queue is empty or invalid.")

found = {row["title"].strip().casefold() for row in rows}
missing = (REJECT | RESEARCH) - found

if missing:
    raise SystemExit(f"Titles not found; nothing changed: {sorted(missing)}")

updated = 0

for row in rows:
    title = row["title"].strip().casefold()

    if title in REJECT:
        row["review_status"] = "rejected"
        updated += 1
    elif title in RESEARCH:
        row["review_status"] = "needs_research"
        updated += 1

with QUEUE.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print(f"Cleanup complete. Updated: {updated}")
print("Final review statistics:", dict(Counter(
    row["review_status"] for row in rows
)))
