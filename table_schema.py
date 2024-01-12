import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('BooksDataFolder/books.db')
cursor = conn.cursor()

# Retrieve the schema of the 'books' table
cursor.execute("PRAGMA table_info(books)")
schema = cursor.fetchall()

# Print out the schema
for column in schema:
    print(column)

# Close the database connection
conn.close()
