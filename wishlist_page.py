# FINALIZED
import os
import sqlite3
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout, QScrollArea, \
    QMessageBox, QSizePolicy
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtCore import Qt


import threading
import json
import requests
from PySide6.QtCore import QThread, Signal

class ApiThread(QThread):
    result_signal = Signal(str, str, str)  # title, author, cover_path

    def __init__(self, title, author, api_key, wishlist_dir):
        QThread.__init__(self)
        self.title = title
        self.author = author
        self.api_key = api_key
        self.wishlist_dir = wishlist_dir


    def run(self):
        title_query = '+'.join(self.title.split())
        author_query = '+'.join(self.author.split())
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title_query}+inauthor:{author_query}&key={self.api_key}"

        print(f"Querying API with URL: {url}")
        response = requests.get(url)

        if response.status_code == 200:
            print("how often is this running")
            data = response.json()
            items = data.get('items')
            if not items:
                self.result_signal.emit(self.title, "", "")
                return

            # Extract book info
            book_info = items[0]['volumeInfo']
            title = book_info.get('title', 'Unknown Title')
            authors = book_info.get('authors', ['Unknown Author'])
            cover_url = book_info.get('imageLinks', {}).get('thumbnail', '')

            # Download the cover image
            image_response = requests.get(cover_url)
            if image_response.status_code == 200:
                cover_path = os.path.join(self.wishlist_dir, f"{title}.jpg")
                with open(cover_path, 'wb') as f:
                    f.write(image_response.content)

                self.result_signal.emit(title, ', '.join(authors), cover_path)
        else:
            self.result_signal.emit(self.title, "", "")

class WishlistPage(QWidget):
    def __init__(self, main_window, parent=None, api_key=''):
        super().__init__()
        self.main_window = main_window
        self.api_key = api_key
        self.wishlist_dir = 'wishlist'
        self.current_row = 0
        self.current_column = 0
        self.max_columns = 4
        self.showMaximized()

        self.initUI()




    def initUI(self):

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor('#42F2C2'))
        self.setPalette(p)


        layout = QVBoxLayout(self)



        # User input to add a book to the wishlist
        self.add_book_input = QLineEdit(self)
        self.add_book_input.setPlaceholderText("Enter a book title to add to your wishlist")
        layout.addWidget(self.add_book_input)

        self.add_author_input = QLineEdit(self)
        self.add_author_input.setPlaceholderText("Enter the books author")
        layout.addWidget(self.add_author_input)

        self.add_book_button = QPushButton("Add to Wishlist", self)
        self.add_book_button.clicked.connect(self.add_book_to_wishlist)
        layout.addWidget(self.add_book_button)

        self.returnHomeButton = QPushButton('Return Home')
        self.returnHomeButton.clicked.connect(self.on_return_home_clicked)
        layout.addWidget(self.returnHomeButton)

        # Scroll area for wishlist items
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.wishlist_layout = QGridLayout()
        self.wishlist_container = QWidget()
        self.wishlist_container.setLayout(self.wishlist_layout)
        self.scroll_area.setWidget(self.wishlist_container)
        layout.addWidget(self.scroll_area)



        self.load_wishlist()

    def add_book_to_wishlist(self):
        title = self.add_book_input.text().strip()
        author = self.add_author_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Warning", "Please enter a book title.")
            return

        wishlist_items = self.get_all_wishlist_items()
        normalized_wishlist = {t.lower(): v for t, v in
                               wishlist_items.items()}  # Normalize existing wishlist titles to lowercase

        if title in normalized_wishlist:
            QMessageBox.information(self, "Information", f"<b>'{title}' is already in your wishlist.</b><br><br><b>Warning:</b> This program does not support\nwishlisting unique books with the same title.")
            return
        # Start the API thread
        self.api_thread = ApiThread(title, author, self.api_key, self.wishlist_dir)
        self.api_thread.result_signal.connect(self.display_wishlist_item)
        self.api_thread.start()

    def truncate_text(self, text, max_length):
        return (text[:max_length - 3] + '...') if len(text) > max_length else text

    def display_wishlist_item(self, title, author, cover_path):
        # Create a container widget and a layout for each wishlist item
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)

        # Set the cover image
        cover_label = QLabel(self)
        cover_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cover_label.setAlignment(Qt.AlignCenter)
        if cover_path and os.path.exists(cover_path):
            pixmap = QPixmap(cover_path)
            cover_label.setPixmap(pixmap.scaled(150, 225, Qt.KeepAspectRatio))
            self.save_wishlist_item(title, author, cover_path)
        else:
            cover_label.setText("Cover not loaded")

        remove_button = QPushButton("Remove", self)
        remove_button.clicked.connect(lambda: self.confirm_removal(title))
        remove_button.setMaximumWidth(50)  # Adjust the width as needed
        remove_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        item_layout.addWidget(remove_button, 0, Qt.AlignCenter)
        item_layout.addWidget(cover_label, 0, Qt.AlignCenter)

        # Add the title and author labels
        truncated_author = self.truncate_text(author, 37)

        title_label = QLabel(f"Title: {title}")
        author_label = QLabel(f"Author: {truncated_author}")


        title_label.setAlignment(Qt.AlignCenter)
        author_label.setAlignment(Qt.AlignCenter)
        item_layout.addWidget(title_label)
        item_layout.addWidget(author_label)

        # Add some spacing
        item_layout.addStretch()

        # Determine the next available position in the grid
        row, col = self.get_next_available_grid_position()
        self.wishlist_layout.addWidget(item_widget, row, col)

    def save_wishlist_item(self, title, author, cover_path):
        # Assuming you have a method to get all wishlist items
        wishlist_items = self.get_all_wishlist_items()
        wishlist_items[title] = {'author': author, 'cover_path': cover_path}

        with open('wishlist.json', 'w') as f:
            json.dump(wishlist_items, f)

    def get_all_wishlist_items(self):
        if os.path.exists('wishlist.json'):
            with open('wishlist.json', 'r') as f:
                return json.load(f)
        return {}

    def load_wishlist(self):
        wishlist_items = self.get_all_wishlist_items()
        for title, info in wishlist_items.items():
            self.display_wishlist_item(title, info['author'], info['cover_path'])

    def get_next_available_grid_position(self):
        # Returns the next available position in the grid
        position = (self.current_row, self.current_column)
        self.current_column += 1
        if self.current_column >= self.max_columns:
            self.current_column = 0
            self.current_row += 1
        return position


    def on_return_home_clicked(self):

        self.main_window.show_home_page()

    def confirm_removal(self, title):
        reply = QMessageBox.question(self, 'Remove Book',
                                     f"Are you sure you want to remove '{title}' from your wishlist?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.remove_book_from_wishlist(title)

    def remove_book_from_wishlist(self, title):
        # Remove the book from the JSON file and update the UI
        wishlist_items = self.get_all_wishlist_items()
        if title in wishlist_items:
            del wishlist_items[title]
            with open('wishlist.json', 'w') as f:
                json.dump(wishlist_items, f)
            self.refresh_wishlist_display()

    def refresh_wishlist_display(self):
        # Clear the existing widgets
        for i in reversed(range(self.wishlist_layout.count())):
            widget_to_remove = self.wishlist_layout.itemAt(i).widget()
            # Remove the widget from the layout
            self.wishlist_layout.removeWidget(widget_to_remove)
            # Delete the widget
            widget_to_remove.deleteLater()

        # Reset the grid position counters
        self.current_row = 0
        self.current_column = 0

        # Reload the wishlist
        self.load_wishlist()

