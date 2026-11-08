from booklens import create_app
from booklens.database import get_db, init_db


def test_init_db_creates_all_tables(tmp_path):
    app = create_app(
        "testing",
        {"DATABASE": str(tmp_path / "test.db")}
    )

    with app.app_context():
        init_db()
        db = get_db()

        tables = {
            row["name"]
            for row in db.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()
        }

    expected_tables = {
        "works",
        "authors",
        "work_authors",
        "concepts",
        "work_concepts",
        "relationship_types",
        "work_relationships",
        "sources",
        "work_concept_sources",
        "relationship_sources",
    }

    assert expected_tables.issubset(tables)


def test_foreign_keys_are_enabled(tmp_path):
    app = create_app(
        "testing",
        {"DATABASE": str(tmp_path / "test.db")}
    )

    with app.app_context():
        db = get_db()

        result = db.execute(
            "PRAGMA foreign_keys"
        ).fetchone()

    assert result[0] == 1
