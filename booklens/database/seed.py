from booklens.database import get_db


AUTHORS = [
    ("Fyodor Dostoevsky", 1821, 1881),
    ("Albert Camus", 1913, 1960),
    ("Franz Kafka", 1883, 1924),
    ("Virginia Woolf", 1882, 1941),
    ("George Orwell", 1903, 1950),
]


WORKS = [
    ("Crime and Punishment", 1866, "ru"),
    ("The Stranger", 1942, "fr"),
    ("The Metamorphosis", 1915, "de"),
    ("Mrs Dalloway", 1925, "en"),
    ("Nineteen Eighty-Four", 1949, "en"),
]


CONCEPTS = [
    ("Alienation", "theme"),
    ("Guilt", "theme"),
    ("Freedom", "philosophical_idea"),
    ("Absurdism", "philosophical_idea"),
    ("Psychological realism", "literary_movement"),
    ("Totalitarianism", "theme"),
]


RELATIONSHIP_TYPES = [
    (
        "thematic_parallel",
        "Thematic parallel",
        "Two works explore a related theme."
    ),
    (
        "philosophical_parallel",
        "Philosophical parallel",
        "Two works explore related philosophical questions."
    ),
    (
        "literary_influence",
        "Literary influence",
        "One work demonstrably influenced another."
    ),
]


def seed_database():
    """Insert initial BookLens records without duplicating them."""

    db = get_db()

    with db:
        # Insert authors.
        for name, birth, death in AUTHORS:
            existing = db.execute(
                "SELECT id FROM authors WHERE name = ?",
                (name,)
            ).fetchone()

            if existing is None:
                db.execute(
                    """
                    INSERT INTO authors (name, birth_year, death_year)
                    VALUES (?, ?, ?)
                    """,
                    (name, birth, death)
                )

        # Insert works.
        for title, year, language in WORKS:
            existing = db.execute(
                """
                SELECT id FROM works
                WHERE title = ?
                AND publication_year = ?
                AND language = ?
                """,
                (title, year, language)
            ).fetchone()

            if existing is None:
                db.execute(
                    """
                    INSERT INTO works (title, publication_year, language)
                    VALUES (?, ?, ?)
                    """,
                    (title, year, language)
                )

        # Connect each work to its author.
        work_author_pairs = [
            ("Crime and Punishment", 1866, "Fyodor Dostoevsky"),
            ("The Stranger", 1942, "Albert Camus"),
            ("The Metamorphosis", 1915, "Franz Kafka"),
            ("Mrs Dalloway", 1925, "Virginia Woolf"),
            ("Nineteen Eighty-Four", 1949, "George Orwell"),
        ]

        for title, year, author_name in work_author_pairs:
            work = db.execute(
                """
                SELECT id FROM works
                WHERE title = ? AND publication_year = ?
                """,
                (title, year)
            ).fetchone()

            author = db.execute(
                "SELECT id FROM authors WHERE name = ?",
                (author_name,)
            ).fetchone()

            db.execute(
                """
                INSERT OR IGNORE INTO work_authors
                    (work_id, author_id, role)
                VALUES (?, ?, 'author')
                """,
                (work["id"], author["id"])
            )

        # Insert concepts.
        for name, category in CONCEPTS:
            db.execute(
                """
                INSERT OR IGNORE INTO concepts (name, category)
                VALUES (?, ?)
                """,
                (name, category)
            )

        # Insert relationship types.
        for code, name, description in RELATIONSHIP_TYPES:
            db.execute(
                """
                INSERT OR IGNORE INTO relationship_types
                    (code, name, description)
                VALUES (?, ?, ?)
                """,
                (code, name, description)
            )
