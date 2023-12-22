import sqlite3
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from book_list_page import BookListPage
from home_page import HomePage
from spreadsheet_loader import initialize_database, read_spreadsheet, write_to_database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.showMaximized()
        self.setWindowTitle('Book App')

        # Create instances of HomePage and BookListPage once and keep them
        self.homePage = HomePage(self)
        self.bookListPage = BookListPage(self)

        # Start with the home page
        self.setCentralWidget(self.homePage)

    def show_book_list_page(self):
        # Switch to the book list page
        self.bookListPage = BookListPage(self)
        self.setCentralWidget(self.bookListPage)

    def show_home_page(self):
        # Switch back to the home page
        self.homePage = HomePage(self)
        self.setCentralWidget(self.homePage)

def main():
    initialize_database()  # Initialize the database

    # Create a connection to the SQLite database
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()

    # Check if the 'books' table has any data
    cursor.execute("SELECT COUNT(*) FROM books")
    data_count = cursor.fetchone()[0]

    if data_count == 0:
        # The database is empty, so import data from the spreadsheet
        excel_path = "C:/Users/Steve/Downloads/finished_spreadsheet.xlsx"  # Update this path
        df = read_spreadsheet(excel_path)  # Read data from spreadsheet
        write_to_database(df)  # Write data to database

    # Close the database connection
    conn.close()

    # Continue with the rest of your application setup
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()
