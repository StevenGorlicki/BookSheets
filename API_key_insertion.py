from PySide6.QtCore import QSize
from PySide6.QtWidgets import QDialog, QLineEdit, QLabel, QVBoxLayout, QPushButton


class ApiKeyInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter API Key")
        self.setMinimumSize(QSize(605, 300))  # Set the minimum size of the dialog
        self.layout = QVBoxLayout(self)

        self.label = QLabel(" Please enter your API key to display book covers and information from Google Books. \n\n\n Go to: https://console.cloud.google.com/apis/credentials?pli=1&project=eminent-bond-409100 \n\n\n Click Create Credentials, API Key, and you're done!")
        self.layout.addWidget(self.label)

        self.api_key_input = QLineEdit(self)
        self.layout.addWidget(self.api_key_input)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.submit_api_key)
        self.layout.addWidget(self.submit_button)

    def submit_api_key(self):
        api_key = self.api_key_input.text().strip()
        if api_key:
            with open('api_key.txt', 'w') as file:
                file.write(api_key)
            self.accept()