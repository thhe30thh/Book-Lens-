import sqlite3
from pathlib import Path

DATABASE_NAME = Path(__file__).resolve().parent / "booklens.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables():
    connection = get_connection()

    connection.executescript("""
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            biography TEXT
        );

        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author_id INTEGER,
            publication_year INTEGER,
            genre TEXT,
            literary_movement TEXT,
            description TEXT,
            FOREIGN KEY (author_id) REFERENCES authors(id)
        );

        CREATE TABLE IF NOT EXISTS themes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS book_themes (
            book_id INTEGER,
            theme_id INTEGER,
            PRIMARY KEY (book_id, theme_id),
            FOREIGN KEY (book_id) REFERENCES books(id),
            FOREIGN KEY (theme_id) REFERENCES themes(id)
        );

        CREATE TABLE IF NOT EXISTS book_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            related_book_id INTEGER NOT NULL,
            relationship_type TEXT NOT NULL,
            explanation TEXT,
            FOREIGN KEY (book_id) REFERENCES books(id),
            FOREIGN KEY (related_book_id) REFERENCES books(id),
            UNIQUE (book_id, related_book_id, relationship_type)
        );
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    print("BookLens database created successfully!")