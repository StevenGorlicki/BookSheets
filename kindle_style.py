from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QScrollArea, QSizePolicy
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import sqlite3
import json
import os
import requests

class BooksPage(QWidget):
    def __init__(self, parent=None, api_key=''):
        super().__init__(parent)
        self.api_key = api_key
        self.cached_covers_file = 'cached_covers.json'
        self.cached_covers = self.load_cached_covers()
        self.initUI()

    def initUI(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        self.grid_layout = QGridLayout()
        self.grid_layout.setHorizontalSpacing(10)  # Adjust spacing as needed
        self.grid_layout.setVerticalSpacing(100)  # Adjust spacing as needed

        container = QWidget()
        container.setLayout(self.grid_layout)
        scroll.setWidget(container)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        self.display_books()

    def load_cached_covers(self):
        if os.path.exists(self.cached_covers_file):
            with open(self.cached_covers_file, 'r') as file:
                return json.load(file)
        return {}

    def save_cached_covers(self):
        with open(self.cached_covers_file, 'w') as file:
            json.dump(self.cached_covers, file)

    def get_book_cover_url(self, title):
        # First, try to get the cover URL from the cached data
        cached_url = self.cached_covers.get(title)
        if cached_url:
            return cached_url

        # If the cover URL is not cached, fetch it from the API
        title_query = '+'.join(title.split())
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title_query}&key={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
            data = response.json()
            items = data.get('items')

            if not items:
                print(f"No cover found for title: {title}")
                return None

            cover_url = items[0]['volumeInfo'].get('imageLinks', {}).get('thumbnail')

            # Cache the new cover URL
            self.cached_covers[title] = cover_url
            self.save_cached_covers()  # Make sure to implement this method to save the cache to a file

            return cover_url
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")

        return None

    def display_books(self):
        conn = sqlite3.connect('books.db')
        cursor = conn.cursor()
        cursor.execute("SELECT title, author FROM books")
        books = cursor.fetchall()
        conn.close()

        for i, (title, author) in enumerate(books):
            cover_url = self.get_book_cover_url(title)
            cover_label = QLabel(self)
            cover_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            if cover_url:
                pixmap = QPixmap(cover_url)  # Assuming the cover_url is a local file path
                cover_label.setPixmap(pixmap.scaled(100, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                cover_label.setText("Cover not loaded")
            self.grid_layout.addWidget(cover_label, i, 0)

            title_label = QLabel(f"Title: {title}")
            author_label = QLabel(f"Author: {author}")
            self.grid_layout.addWidget(title_label, i, 1)
            self.grid_layout.addWidget(author_label, i, 2)
