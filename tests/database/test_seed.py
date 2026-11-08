from booklens import create_app
from booklens.database import get_db, init_db
from booklens.database.seed import seed_database


def test_seed_database_inserts_initial_records(tmp_path):
    app = create_app(
        "testing",
        {"DATABASE": str(tmp_path / "seed_test.db")}
    )

    with app.app_context():
        init_db()
        seed_database()

        db = get_db()

        assert db.execute("SELECT COUNT(*) FROM authors").fetchone()[0] == 5
        assert db.execute("SELECT COUNT(*) FROM works").fetchone()[0] == 5
        assert db.execute("SELECT COUNT(*) FROM concepts").fetchone()[0] == 6
        assert db.execute("SELECT COUNT(*) FROM relationship_types").fetchone()[0] == 3
        assert db.execute("SELECT COUNT(*) FROM work_authors").fetchone()[0] == 5


def test_seed_database_is_idempotent(tmp_path):
    app = create_app(
        "testing",
        {"DATABASE": str(tmp_path / "seed_repeat_test.db")}
    )

    with app.app_context():
        init_db()

        seed_database()
        seed_database()

        db = get_db()

        assert db.execute("SELECT COUNT(*) FROM authors").fetchone()[0] == 5
        assert db.execute("SELECT COUNT(*) FROM works").fetchone()[0] == 5
        assert db.execute("SELECT COUNT(*) FROM concepts").fetchone()[0] == 6
        assert db.execute("SELECT COUNT(*) FROM relationship_types").fetchone()[0] == 3
        assert db.execute("SELECT COUNT(*) FROM work_authors").fetchone()[0] == 5
