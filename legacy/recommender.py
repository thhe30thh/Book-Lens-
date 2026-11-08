from database import get_connection


def recommend_books(book_id):
    connection = get_connection()

    query = """
        SELECT
            books.id,
            books.title,
            authors.name AS author,
            COUNT(DISTINCT shared.theme_id) AS shared_themes,
            GROUP_CONCAT(DISTINCT themes.name) AS themes
        FROM books
        JOIN authors ON books.author_id = authors.id
        JOIN book_themes AS shared
            ON books.id = shared.book_id
        JOIN themes ON shared.theme_id = themes.id
        WHERE shared.theme_id IN (
            SELECT theme_id
            FROM book_themes
            WHERE book_id = ?
        )
        AND books.id != ?
        GROUP BY books.id
        ORDER BY shared_themes DESC
    """

    results = connection.execute(
        query, (book_id, book_id)
    ).fetchall()

    connection.close()

    recommendations = []

    for book in results:
        recommendations.append({
            "id": book["id"],
            "title": book["title"],
            "author": book["author"],
            "shared_themes": book["shared_themes"],
            "themes": book["themes"].split(",")
        })

    return recommendations


if __name__ == "__main__":
    results = recommend_books(1)

    for book in results:
        print(f"\nRecommendation: {book['title']}")
        print(f"Author: {book['author']}")
        print(f"Shared themes: {', '.join(book['themes'])}")