# FINALIZED
import os
import sqlite3
from queue import Queue

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout, QScrollArea, \
    QMessageBox, QSizePolicy
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtCore import Qt, QTimer

import threading
import json
import requests
from PySide6.QtCore import QThread, Signal
from fetch_db_titles import fetch_book_titles_from_db

class ApiThread(QThread):
    result_signal = Signal(str, str, str)  # title, author, cover_path

    def __init__(self, books, api_key, covers_dir):
        QThread.__init__(self)
        self.books = books
        self.api_key = api_key
        self.covers_dir = covers_dir

    def run(self):
        try:
            for title, author in self.books:
                title_query = '+'.join(title.split())
                author_query = '+'.join(author.split())
                url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title_query}+inauthor:{author_query}&key={self.api_key}"
                print(url)
                response = requests.get(url)

                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items')
                    print(items)
                    if not items:
                        self.result_signal.emit(title, "", "")
                        continue

                    for item in items:
                        book_info = item.get('volumeInfo', {})
                        current_authors = book_info.get('authors', ['Unknown Author'])
                        cover_url = book_info.get('imageLinks', {}).get('thumbnail')

                        if cover_url:
                            image_response = requests.get(cover_url)
                            if image_response.status_code == 200:
                                cover_path = os.path.join(self.covers_dir, f"{title}.jpg")
                                with open(cover_path, 'wb') as f:
                                    f.write(image_response.content)
                                self.result_signal.emit(title, ', '.join(current_authors), cover_path)
                                break


                    else:
                        self.result_signal.emit(title, author, "")
                else:
                    self.result_signal.emit(title, author, "")
        except Exception as e:
            print(f"Error in ApiThread: {e}")


class BooksPage(QWidget):
    def __init__(self, main_window, parent=None, api_key=''):
        super().__init__()
        self.main_window = main_window
        self.api_key = api_key
        self.covers_dir = 'covers'
        self.queue = Queue()
        self.api_thread = None
        self.current_row = 0
        self.current_column = 0
        self.max_columns = 4  # Adjust as needed
        self.initUI()

    def initUI(self):

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor('#42F2C2'))
        self.setPalette(p)


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
        books = fetch_book_titles_from_db()
        for book in books:
            title = book['title']
            author = book['author']
            cover_path = os.path.join(self.covers_dir, f"{title}.jpg")
            if os.path.exists(cover_path):
                self.display_book_item(title, author, cover_path)
            else:
                self.queue.put((title, author))  # Put a tuple of title and author in the queue
        QTimer.singleShot(0, self.process_next)

    def process_next(self):
        if not self.queue.empty() and (self.api_thread is None or not self.api_thread.isRunning()):
            title, author = self.queue.get()
            cover_path = os.path.join(self.covers_dir, f"{title}.jpg")
            self.api_thread = ApiThread([(title, author)], self.api_key, self.covers_dir)
            self.api_thread.result_signal.connect(self.display_book_item)
            self.api_thread.finished.connect(self.process_next)  # When one thread finishes, process the next
            self.api_thread.start()
        elif self.queue.empty() and self.api_thread is not None:
            self.api_thread.finished.disconnect(self.process_next)

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
