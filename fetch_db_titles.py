import sqlite3


def fetch_book_titles_from_db():
    conn = sqlite3.connect('BooksDataFolder/books.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title, author FROM books")  # Fetch both titles and authors
    books = [{'title': row[0], 'author': row[1]} for row in cursor.fetchall()]
    conn.close()
    return books[1:]