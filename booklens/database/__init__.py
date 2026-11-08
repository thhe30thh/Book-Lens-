import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    """Get the database connection for the current request."""

    if "db" not in g:
        database_path = current_app.config["DATABASE"]

        connection = sqlite3.connect(database_path)

        connection.row_factory = sqlite3.Row

        connection.execute("PRAGMA foreign_keys = ON")

        g.db = connection

    return g.db


def close_db(error=None):
    """Close the database connection when the app context ends."""

    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Create all database tables using schema.sql."""

    db = get_db()

    schema_path = Path(__file__).with_name("schema.sql")

    schema = schema_path.read_text(encoding="utf-8")

    db.executescript(schema)


def init_app(app):
    """Register database configuration and cleanup."""

    app.config.setdefault(
        "DATABASE",
        str(Path(app.instance_path) / "booklens.db")
    )

    app.teardown_appcontext(close_db)
