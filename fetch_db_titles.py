import sqlite3


def fetch_book_titles_from_db():
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM books")  # Assuming 'books' is your table name
    titles = [row[0] for row in cursor.fetchall()]
    conn.close()
    return titles[1:]