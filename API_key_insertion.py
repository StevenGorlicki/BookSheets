from PySide6.QtCore import QSize
from PySide6.QtWidgets import QDialog, QLineEdit, QLabel, QVBoxLayout, QPushButton
import configparser
import os

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
        self.submit_button.clicked.connect(self.accept)  # We will get the API key after the dialog is accepted
        self.layout.addWidget(self.submit_button)

    def get_api_key(self):
        return self.api_key_input.text().strip()

    @staticmethod
    def save_api_key(api_key):
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'ApiKey': api_key}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    @staticmethod
    def load_api_key():
        if not os.path.exists('config.ini'):
            return None
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config['DEFAULT'].get('ApiKey', None)