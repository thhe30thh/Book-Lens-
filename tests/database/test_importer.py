import pytest

from booklens import create_app
from booklens.database import get_db, init_db
from booklens.database.importer import import_works_from_csv


def create_test_app(tmp_path):
    app = create_app(
        "testing",
        {"DATABASE": str(tmp_path / "import_test.db")}
    )

    with app.app_context():
        init_db()

    return app


def test_importer_adds_books_and_authors(tmp_path):
    app = create_test_app(tmp_path)

    csv_file = tmp_path / "books.csv"
    csv_file.write_text(
        "title,publication_year,language,authors\n"
        "The Trial,1925,de,Franz Kafka\n"
        "The Plague,1947,fr,Albert Camus\n",
        encoding="utf-8"
    )

    with app.app_context():
        result = import_works_from_csv(csv_file)
        db = get_db()

        assert result["works_imported"] == 2
        assert result["authors_imported"] == 2
        assert result["connections_created"] == 2

        assert db.execute("SELECT COUNT(*) FROM works").fetchone()[0] == 2
        assert db.execute("SELECT COUNT(*) FROM authors").fetchone()[0] == 2


def test_importer_supports_multiple_authors(tmp_path):
    app = create_test_app(tmp_path)

    csv_file = tmp_path / "books.csv"
    csv_file.write_text(
        "title,publication_year,language,authors\n"
        "Collaborative Work,2020,en,Author One;Author Two\n",
        encoding="utf-8"
    )

    with app.app_context():
        result = import_works_from_csv(csv_file)
        db = get_db()

        assert result["authors_imported"] == 2
        assert result["connections_created"] == 2
        assert db.execute("SELECT COUNT(*) FROM work_authors").fetchone()[0] == 2


def test_importer_does_not_duplicate_records(tmp_path):
    app = create_test_app(tmp_path)

    csv_file = tmp_path / "books.csv"
    csv_file.write_text(
        "title,publication_year,language,authors\n"
        "The Trial,1925,de,Franz Kafka\n",
        encoding="utf-8"
    )

    with app.app_context():
        first = import_works_from_csv(csv_file)
        second = import_works_from_csv(csv_file)
        db = get_db()

        assert first["works_imported"] == 1
        assert second["works_imported"] == 0
        assert second["authors_imported"] == 0
        assert second["connections_created"] == 0

        assert db.execute("SELECT COUNT(*) FROM works").fetchone()[0] == 1


def test_importer_rejects_missing_columns(tmp_path):
    app = create_test_app(tmp_path)

    csv_file = tmp_path / "invalid.csv"
    csv_file.write_text(
        "title,authors\n"
        "The Trial,Franz Kafka\n",
        encoding="utf-8"
    )

    with app.app_context():
        with pytest.raises(ValueError, match="Missing CSV columns"):
            import_works_from_csv(csv_file)


def test_importer_rejects_invalid_year(tmp_path):
    app = create_test_app(tmp_path)

    csv_file = tmp_path / "invalid.csv"
    csv_file.write_text(
        "title,publication_year,language,authors\n"
        "The Trial,not-a-year,de,Franz Kafka\n",
        encoding="utf-8"
    )

    with app.app_context():
        with pytest.raises(ValueError, match="invalid publication year"):
            import_works_from_csv(csv_file)
