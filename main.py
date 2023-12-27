# FINALIZED MAYBE
import sqlite3
import sys
import os

from API_key_insertion import ApiKeyInputDialog
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

from InputPage import SpreadsheetInputPage
from book_list_page import BookListPage
from home_page import HomePage
from spreadsheet_loader import initialize_database, read_spreadsheet, write_to_database
from kindle_style import BooksPage
from wishlist_page import WishlistPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = None
        create_directory_if_not_exists('covers')
        create_directory_if_not_exists('wishlist')
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

    def check_and_input_api_key(self):
        if not self.api_key:  # Check if the API key is not set
            dialog = ApiKeyInputDialog(self)
            if dialog.exec_():
                self.api_key = dialog.get_api_key()  # Get the API key from the dialog

    def is_api_key_saved(self):
        return bool(self.api_key)  # Check if the API key attribute is set

    def get_saved_api_key(self):
        return self.api_key



    def closeEvent(self, event):

        if self.bookListPage.changed_rows:
            reply = QMessageBox.question(self, 'Save Changes',
                                         "You have unsaved changes. Would you like to save them before exiting?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                self.bookListPage.save_changes_to_db()
                event.accept()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

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

    def show_books_page(self):
        api_key = self.get_saved_api_key()
        self.booksPage = BooksPage(self, api_key=api_key)
        self.setCentralWidget(self.booksPage)
        self.showMaximized()

    def show_wishlist_page(self):
        api_key = self.get_saved_api_key()
        self.wishlistPage = WishlistPage(self, api_key=api_key)
        self.setCentralWidget(self.wishlistPage)
        self.showMaximized()


def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

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

    # Don't show the main window until we've checked the API key
    mainWindow.check_and_input_api_key()  # This will prompt for the API key if not set

    # Now, depending on the API key and data count, decide what to do next
    if mainWindow.is_api_key_saved():
        if data_count == 0:
            mainWindow.show_spreadsheet_input_page()
        else:
            mainWindow.show_home_page()
        mainWindow.show()  # Now we show the main window
    else:
        # If the API key still isn't set, we inform the user and exit
        QMessageBox.warning(None, "API Key Required", "An API key is required to use this application.")
        sys.exit()  # Exit the application

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()












