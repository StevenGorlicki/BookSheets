import pandas as pd
import sqlite3

def initialize_database(db_path='books.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            "Memorable Characters" TEXT,
            audible TEXT,
            narrator TEXT,
            "Best Quotes" TEXT,
            "Memorable Content" TEXT,
            recommend TEXT,
            service TEXT
        );
    """)

    conn.commit()
    conn.close()


def load_book_data(excel_path):
    df = pd.read_excel(excel_path, header=None, skiprows=1)
    df = df.fillna('')  # Replace NaN values with an empty string
    df = df.iloc[1:]  # Adjustsload_data_from the DataFrame to skip the first row of data
    df.reset_index(drop=True, inplace=True)
    return df

def read_spreadsheet(excel_path):
    df = pd.read_excel(excel_path, engine='openpyxl')
    df = df.iloc[:, :-1]
    return df

def write_to_database(df, db_path='books.db'):
    conn = sqlite3.connect(db_path)

    # Check for null or empty titles and handle them
    df = df.dropna(subset=['title'])  # Drop rows where title is NaN
    df['title'] = df['title'].fillna('Unknown Title')  # Replace NaN with a default value

    df.to_sql('books', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()

# You can add additional functions or code here if needed.
