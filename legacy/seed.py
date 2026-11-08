from database import get_connection


def add_author(connection, name, biography):
    cursor = connection.execute(
        "SELECT id FROM authors WHERE name = ?", (name,)
    )

    author = cursor.fetchone()

    if author:
        return author["id"]

    cursor = connection.execute(
        "INSERT INTO authors (name, biography) VALUES (?, ?)",
        (name, biography)
    )

    return cursor.lastrowid


def add_book(connection, title, author_id, year, genre, movement, description):
    cursor = connection.execute(
        "SELECT id FROM books WHERE title = ? AND author_id = ?",
        (title, author_id)
    )

    book = cursor.fetchone()

    if book:
        return book["id"]

    cursor = connection.execute("""
        INSERT INTO books
        (title, author_id, publication_year, genre,
         literary_movement, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, author_id, year, genre, movement, description))

    return cursor.lastrowid


def add_theme(connection, name, description):
    cursor = connection.execute(
        "SELECT id FROM themes WHERE name = ?", (name,)
    )

    theme = cursor.fetchone()

    if theme:
        return theme["id"]

    cursor = connection.execute(
        "INSERT INTO themes (name, description) VALUES (?, ?)",
        (name, description)
    )

    return cursor.lastrowid


def connect_theme(connection, book_id, theme_id):
    connection.execute("""
        INSERT OR IGNORE INTO book_themes (book_id, theme_id)
        VALUES (?, ?)
    """, (book_id, theme_id))


def add_relationship(connection, book1, book2, relationship_type, explanation):
    connection.execute("""
        INSERT OR IGNORE INTO book_relationships
        (book_id, related_book_id, relationship_type, explanation)
        VALUES (?, ?, ?, ?)
    """, (book1, book2, relationship_type, explanation))


def seed_database():
    connection = get_connection()

    try:
        dostoevsky = add_author(
            connection,
            "Fyodor Dostoevsky",
            "Russian novelist known for exploring psychology, morality and philosophy."
        )

        camus = add_author(
            connection,
            "Albert Camus",
            "French-Algerian writer and philosopher associated with absurdism."
        )

        crime = add_book(
            connection, "Crime and Punishment", dostoevsky,
            1866, "Psychological fiction", "Realism",
            "A psychological novel exploring guilt, morality and redemption."
        )

        underground = add_book(
            connection, "Notes from Underground", dostoevsky,
            1864, "Philosophical fiction", "Realism",
            "A narrator reflects on isolation, freedom and human irrationality."
        )

        stranger = add_book(
            connection, "The Stranger", camus,
            1942, "Philosophical fiction", "Absurdism",
            "A novel exploring alienation and the absurdity of existence."
        )

        guilt = add_theme(
            connection, "Guilt",
            "The psychological and moral burden of wrongdoing."
        )

        alienation = add_theme(
            connection, "Alienation",
            "Separation from society, others or oneself."
        )

        freedom = add_theme(
            connection, "Freedom",
            "The ability to make choices and confront their consequences."
        )

        connect_theme(connection, crime, guilt)
        connect_theme(connection, crime, alienation)
        connect_theme(connection, underground, alienation)
        connect_theme(connection, underground, freedom)
        connect_theme(connection, stranger, alienation)
        connect_theme(connection, stranger, freedom)

        add_relationship(
            connection, crime, underground,
            "shared_author",
            "Both novels explore psychological conflict and the complexity of human behavior."
        )

        add_relationship(
            connection, underground, stranger,
            "shared_theme",
            "Both examine alienation and the individual's relationship with society."
        )

        connection.commit()
        print("BookLens literary data added successfully!")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    seed_database()