import pandas as pd
import sqlite3

def export_database_to_spreadsheet(db_path='books.db', output_path='exported_books.xlsx'):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # Query all data from the 'books' table and load it into a DataFrame
    query = "SELECT * FROM books"
    df = pd.read_sql_query(query, conn)

    df = df.iloc[:, 1:]

    # Close the database connection
    conn.close()

    # Write the DataFrame to an Excel file
    df.to_excel(output_path, index=False)