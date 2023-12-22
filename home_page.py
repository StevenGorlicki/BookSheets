# home_page.py
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QLineEdit, QLabel, QHBoxLayout


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Add search fields and dropdowns
        self.add_search_field(layout, "Title")
        self.add_search_field(layout, "Author")
        self.add_search_field(layout, "Narrator")

        # Existing button to go to the book list
        self.button = QPushButton('Go to Book List', self)
        self.button.clicked.connect(self.on_button_clicked)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def add_search_field(self, layout, label_text):
        # Create a horizontal layout for each search field
        h_layout = QHBoxLayout()

        # Label
        label = QLabel(label_text, self)
        h_layout.addWidget(label)

        # Line edit for search input
        search_input = QLineEdit(self)
        h_layout.addWidget(search_input)

        # Dropdown for selecting the service
        service_dropdown = QComboBox(self)
        service_dropdown.addItem("Service:")  # Non-selectable item
        service_dropdown.addItems(["Kindle Unlimited", "Audible", "Hoopla", "Chirp"])  # Actual selectable items
        service_dropdown.currentIndexChanged.connect(
            lambda: self.on_service_selected(search_input.text(), service_dropdown.currentText(), service_dropdown))
        h_layout.addWidget(service_dropdown)
        # Add the horizontal layout to the main layout
        layout.addLayout(h_layout)

    def on_service_selected(self, search_term, service_name, dropdown):
        # Map service names to URLs
        if service_name == "Service:":
            return
        service_urls = {
            "Kindle Unlimited": "https://www.amazon.com/Browse-Kindle-Unlimited-Books/b?ie=UTF8&node=9069934011",
            "Audible": "https://www.audible.com/",
            "Hoopla": "https://www.hoopladigital.com/home",
            "Chirp": "https://www.chirpbooks.com/"
        }
        url = QUrl(service_urls.get(service_name, ""))
        if url.isValid():
            QDesktopServices.openUrl(url)

        dropdown.setCurrentIndex(0)

    def on_button_clicked(self):
        self.parent().show_book_list_page()