from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from spreadsheet_loader import read_spreadsheet, write_to_database
class SpreadsheetInputPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("Enter the path of your spreadsheet:")
        layout.addWidget(self.label)

        self.line_edit = QLineEdit()
        layout.addWidget(self.line_edit)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.on_submit_clicked)
        layout.addWidget(self.submit_button)

    def on_submit_clicked(self):
        spreadsheet_path = self.line_edit.text()
        if spreadsheet_path:
            # Load spreadsheet and update database
            df = read_spreadsheet(spreadsheet_path)
            write_to_database(df)
            self.main_window.show_home_page()  # Show the main page after updating the database
        else:
            # Handle the case where the path is empty
            self.label.setText("Please enter a valid path.")
