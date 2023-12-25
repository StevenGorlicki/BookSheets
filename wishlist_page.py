import os
import sqlite3
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout, QScrollArea, \
    QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

import threading
import json
import requests
from PySide6.QtCore import QThread, Signal

class ApiThread(QThread):
    result_signal = Signal(str, str, str)  # title, author, cover_path

    def __init__(self, title, api_key, wishlist_dir):
        QThread.__init__(self)
        self.title = title
        self.api_key = api_key
        self.wishlist_dir = wishlist_dir

    def run(self):
        title_query = '+'.join(self.title.split())
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title_query}&key={self.api_key}"
        print(f"Querying API with URL: {url}")
        response = requests.get(url)

        if response.status_code == 200:
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
    def __init__(self, parent=None, api_key=''):
        super().__init__(parent)
        self.api_key = api_key
        self.wishlist_dir = 'wishlist'
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # User input to add a book to the wishlist
        self.add_book_input = QLineEdit(self)
        self.add_book_input.setPlaceholderText("Enter a book title to add to your wishlist")
        layout.addWidget(self.add_book_input)

        self.add_book_button = QPushButton("Add to Wishlist", self)
        self.add_book_button.clicked.connect(self.add_book_to_wishlist)
        layout.addWidget(self.add_book_button)

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
        if not title:
            QMessageBox.warning(self, "Warning", "Please enter a book title.")
            return

        # Start the API thread
        self.api_thread = ApiThread(title, self.api_key, self.wishlist_dir)
        self.api_thread.result_signal.connect(self.display_wishlist_item)
        self.api_thread.start()

    def display_wishlist_item(self, title, author, cover_path):
        if not author and not cover_path:
            QMessageBox.warning(self, "Warning", f"Could not find book: {title}")
            return

        # Display the book cover, title, and author on the wishlist layout
        cover_label = QLabel(self)
        if cover_path and os.path.exists(cover_path):
            pixmap = QPixmap(cover_path)
            cover_label.setPixmap(pixmap.scaled(100, 150, Qt.KeepAspectRatio))
        else:
            cover_label.setText("Cover not loaded")
        self.wishlist_layout.addWidget(cover_label)

        title_label = QLabel(f"Title: {title}")
        author_label = QLabel(f"Author: {author}")
        self.wishlist_layout.addWidget(title_label)
        self.wishlist_layout.addWidget(author_label)

        # Save the wishlist item
        self.save_wishlist_item(title, author, cover_path)

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
