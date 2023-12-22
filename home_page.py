# home_page.py
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QLineEdit, QLabel, QHBoxLayout, QSpacerItem, \
    QSizePolicy, QGridLayout


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QGridLayout()

        # Set the margins and spacing to align items to the top left
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(10)

        # Add search fields and dropdowns
        self.add_search_field(layout, "Title", 0)
        self.add_search_field(layout, "Author", 1)
        self.add_search_field(layout, "Narrator", 2)

        # Existing button to go to the book list
        self.button = QPushButton('Go to Book List', self)
        self.button.clicked.connect(self.on_button_clicked)
        self.button.setMinimumHeight(50)  # Set a minimum height to make the button taller
        layout.addWidget(self.button, 3, 0, 1, 2)  # Span 2 columns

        self.setLayout(layout)

    def add_search_field(self, layout, label_text, row):
        # Increase the font size for the label
        label_font = QFont()
        label_font.setPointSize(12)  # Set font size to 12

        # Label
        label = QLabel(label_text, self)
        label.setFont(label_font)
        layout.addWidget(label, row, 0)

        # Line edit for search input
        search_input = QLineEdit(self)
        search_input.setFont(label_font)
        search_input.setFixedWidth(300)  # Adjust the fixed width if necessary
        layout.addWidget(search_input, row, 1)

        # Dropdown for selecting the service
        service_dropdown = QComboBox(self)
        service_dropdown.setFont(label_font)
        service_dropdown.setFixedWidth(200)  # Adjust the fixed width if necessary
        service_dropdown.addItem("Service:")  # Non-selectable item
        service_dropdown.addItems(["Kindle Unlimited", "Audible", "Hoopla", "Chirp"])  # Actual selectable items
        layout.addWidget(service_dropdown, row, 2)

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