import os
import sqlite3
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout, QScrollArea, \
    QMessageBox, QSizePolicy
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

import threading
import json
import requests
from PySide6.QtCore import QThread, Signal
from fetch_db_titles import fetch_book_titles_from_db

class ApiThread(QThread):
    result_signal = Signal(str, str, str)  # title, author, cover_path

    def __init__(self, titles, api_key, covers_dir):
        QThread.__init__(self)
        self.titles = titles
        self.api_key = api_key
        self.covers_dir = covers_dir

    def run(self):
        for title in self.titles:
            title_query = '+'.join(title.split())
            url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title_query}&key={self.api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                print("how oftern is this running.")
                data = response.json()
                items = data.get('items')
                if not items:
                    self.result_signal.emit(title, "", "")
                    continue

                book_info = items[0]['volumeInfo']
                authors = book_info.get('authors', ['Unknown Author'])
                cover_url = book_info.get('imageLinks', {}).get('thumbnail', '')

                image_response = requests.get(cover_url)
                if image_response.status_code == 200:
                    cover_path = os.path.join(self.covers_dir, f"{title}.jpg")
                    with open(cover_path, 'wb') as f:
                        f.write(image_response.content)
                    self.result_signal.emit(title, ', '.join(authors), cover_path)
                else:
                    self.result_signal.emit(title, ', '.join(authors), "")
            else:
                self.result_signal.emit(title, "", "")



class BooksPage(QWidget):
    def __init__(self, main_window, parent=None, api_key=''):
        super().__init__()
        self.main_window = main_window
        self.api_key = api_key
        self.covers_dir = 'covers'
        self.current_row = 0
        self.current_column = 0
        self.max_columns = 4  # Adjust as needed
        self.initUI()

    def initUI(self):


        # ... rest of the UI setup ...
        layout = QVBoxLayout(self)

        self.returnHomeButton = QPushButton('Return Home')
        self.returnHomeButton.clicked.connect(self.on_return_home_clicked)
        layout.addWidget(self.returnHomeButton)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.books_layout = QGridLayout()
        self.books_container = QWidget()
        self.books_container.setLayout(self.books_layout)
        self.scroll_area.setWidget(self.books_container)
        layout.addWidget(self.scroll_area)
        self.load_owned_books()

    def load_owned_books(self):
        titles = fetch_book_titles_from_db()
        for title in titles:
            cover_path = os.path.join(self.covers_dir, f"{title}.jpg")
            if os.path.exists(cover_path):
                # If the cover image exists, display it directly
                self.display_book_item(title, "", cover_path)
            else:
                # If the cover image does not exist, start the API thread to fetch it
                self.api_thread = ApiThread([title], self.api_key, self.covers_dir)
                self.api_thread.result_signal.connect(self.display_book_item)
                self.api_thread.start()

    def display_book_item(self, title, author, cover_path):
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)

        cover_label = QLabel(self)
        cover_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cover_label.setAlignment(Qt.AlignCenter)
        if cover_path and os.path.exists(cover_path):
            pixmap = QPixmap(cover_path)
            cover_label.setPixmap(pixmap.scaled(150, 225, Qt.KeepAspectRatio))
        else:
            cover_label.setText("Cover not loaded")
        item_layout.addWidget(cover_label, 0, Qt.AlignCenter)

        title_label = QLabel(f"Title: {title}")
        author_label = QLabel(f"Author: {author}")
        title_label.setAlignment(Qt.AlignCenter)
        author_label.setAlignment(Qt.AlignCenter)
        item_layout.addWidget(title_label)
        item_layout.addWidget(author_label)

        item_layout.addStretch()

        row, col = self.get_next_available_grid_position()
        self.books_layout.addWidget(item_widget, row, col)

    def get_next_available_grid_position(self):
        position = (self.current_row, self.current_column)
        self.current_column += 1
        if self.current_column >= self.max_columns:
            self.current_column = 0
            self.current_row += 1
        return position

    def on_return_home_clicked(self):
        self.main_window.show_home_page()
