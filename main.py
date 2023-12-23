import sqlite3
import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QMainWindow

from InputPage import SpreadsheetInputPage
from book_list_page import BookListPage
from home_page import HomePage
from spreadsheet_loader import initialize_database, read_spreadsheet, write_to_database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.homePageSize = QSize(575, 200)

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
        self.showMaximized()

    def show_home_page(self):
        # Switch back to the home page
        self.homePage = HomePage(self)
        self.setCentralWidget(self.homePage)

        # Resize the window to the preferred size for the homepage
        self.resize(self.homePageSize)

        # Move the window to the top left of the screen
        self.move_to_top_left()



    def show_spreadsheet_input_page(self):
        self.spreadsheetInputPage = SpreadsheetInputPage(self)
        self.setCentralWidget(self.spreadsheetInputPage)
        self.center_window()

    def move_to_top_left(self):
        # Get the available geometry of the primary screen
        available_geometry = QApplication.screens()[0].availableGeometry()
        # Move the window to the top left of the available geometry
        self.move(available_geometry.topLeft())

    def center_window(self):
        # Get the rectangle specifying the geometry of the screen
        screen_rect = QApplication.primaryScreen().geometry()
        # Calculate the center point
        center_point = screen_rect.center()
        # Move the window's center to that point
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())


def main():
    initialize_database()  # Initialize the database

    # Create a connection to the SQLite database
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()

    # Check if the 'books' table has any data
    cursor.execute("SELECT COUNT(*) FROM books")
    data_count = cursor.fetchone()[0]

    # Close the database connection
    conn.close()

    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    if data_count == 0:
        mainWindow.show_spreadsheet_input_page()
    else:
        mainWindow.show_home_page()

    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()
