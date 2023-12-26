# FINALIZED
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, QFont, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QLineEdit, QLabel, QGridLayout, QMessageBox


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor('#42F2C2'))
        self.setPalette(p)
        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(10)

        # Create a single dropdown for search, placed at the top
        self.service_dropdown = QComboBox(self)
        self.setup_dropdown(layout)

        # Add search fields without dropdowns
        self.title_input = self.add_search_field(layout, "Title", 1)
        self.author_input = self.add_search_field(layout, "Author", 2)
        self.narrator_input = self.add_search_field(layout, "Narrator", 3)

        # Existing button to go to the book list
        self.button = QPushButton('Open Spreadsheet', self)
        self.button.clicked.connect(self.on_button_clicked)
        self.button.setMinimumHeight(50)  # Set a minimum height to make the button taller
        layout.addWidget(self.button, 4, 0, 1, 2)  # Span 2 columns

        self.booksPageButton = QPushButton('Open Books', self)
        self.booksPageButton.clicked.connect(self.on_books_page_button_clicked)
        self.booksPageButton.setMinimumHeight(50)
        layout.addWidget(self.booksPageButton, 5, 0, 1, 2)
        self.setLayout(layout)

        self.wishlistPageButton = QPushButton('Open Wishlist', self)
        self.wishlistPageButton.clicked.connect(self.on_wishlist_page_button_clicked)
        self.wishlistPageButton.setMinimumHeight(50)
        layout.addWidget(self.wishlistPageButton, 6, 0, 1, 2)
    def add_search_field(self, layout, label_text, row):
        label_font = QFont()
        label_font.setPointSize(12)

        # Label
        label = QLabel(label_text, self)
        label.setFont(label_font)
        layout.addWidget(label, row, 0)

        # Line edit for search input
        search_input = QLineEdit(self)
        search_input.setFont(label_font)
        search_input.setFixedWidth(300)
        layout.addWidget(search_input, row, 1)

        return search_input

    def setup_dropdown(self, layout):
        label_font = QFont()
        label_font.setPointSize(12)

        # Dropdown for selecting the service
        self.service_dropdown.setFont(label_font)
        self.service_dropdown.setFixedWidth(200)
        self.service_dropdown.addItem("Search")
        self.service_dropdown.addItems(["Kindle Unlimited", "Audible", "Hoopla", "Chirp"])
        self.service_dropdown.currentIndexChanged.connect(self.on_service_selected)
        layout.addWidget(self.service_dropdown, 1, 2)

    def on_service_selected(self, index):
        if index > 0:  # Assuming the first item is the non-selectable prompt
            # Gather the search terms from the input fields
            title = self.title_input.text()
            author = self.author_input.text()
            narrator = self.narrator_input.text()

            # Perform the search action
            service_name = self.service_dropdown.currentText()
            self.search_books(title, author, narrator, service_name)

            # Reset the dropdown index after search
            self.service_dropdown.setCurrentIndex(0)

    def search_books(self, title, author, narrator, service_name):
        # Combine title, author, and narrator into a single search query
        search_terms = ' '.join(filter(None, [title, author, narrator])).strip()
        if not search_terms:
            QMessageBox.warning(self, "Warning", "Please enter at least one search term.")
            return

        # Encode the search query for URL
        query = '+'.join(search_terms.split())

        # Map service names to their search URLs
        service_urls = {
            "Kindle Unlimited": f"https://www.amazon.com/s?k={query}",
            "Audible": f"https://www.audible.com/search?keywords={query}",
            "Hoopla": f"https://www.hoopladigital.com/search?q={query}&scope=everything&type=direct",
            "Chirp": f"https://www.chirpbooks.com/search?q={query}"
        }

        url = QUrl(service_urls.get(service_name, ""))
        if url.isValid():
            QDesktopServices.openUrl(url)
        else:
            QMessageBox.critical(self, "Error", "Invalid service selected or URL formation error.")

    def on_button_clicked(self):
        self.parent().show_book_list_page()

    def on_books_page_button_clicked(self):
        self.parent().show_books_page()

    def on_wishlist_page_button_clicked(self):
        self.parent().show_wishlist_page()