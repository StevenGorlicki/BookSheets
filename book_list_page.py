# FINALIZED
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QTableWidgetItem, QPushButton, \
    QHBoxLayout, QLabel, QSpacerItem, QSizePolicy, QLineEdit, QComboBox, QMessageBox, QInputDialog, QMenu
from PySide6.QtCore import Qt
from convert_to_spread import export_database_to_spreadsheet

import os
from pathlib import Path
import sqlite3


class CaseInsensitiveTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        my_text = self.text().strip()
        other_text = other.text().strip()

        if my_text == "" and other_text == "":
            return False
        if my_text == "":
            return False
        if other_text == "":
            return True

        return my_text.lower() < other_text.lower()


class BookListPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.column_widths_file = 'BooksDataFolder/userSettings.txt'  # File path

        self.is_loading_data = False
        self.changed_rows = set()  # Initialize changed_rows here
        self.row_id_map = {}  # Dictionary to map table rows to database IDs

        self.initUI()
        self.load_data_from_db()


    def initUI(self):

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor('#42F2C2'))
        self.setPalette(p)


        mainLayout = QVBoxLayout()

        # Create a table widget
        self.table = QTableWidget(self)
        self.table.setColumnCount(9)

        self.table.itemChanged.connect(self.track_change)  # Connect to track_change

        # Set column headers
        self.table.setHorizontalHeaderLabels([
            "Title", "Author", "Memorable Characters", "Audible",
            "Narrator", "Best Quotes", "Memorable Content",
            "Recommend", "Service"
        ])

        # Define custom widths for each column


        # Enable word wrap in cells
        self.table.setWordWrap(True)

        self.table.horizontalHeader().sectionResized.connect(self.column_resized)

        # Load saved column widths (if any), otherwise set default widths
        self.load_column_widths()


        # Adjust row heights to accommodate wrapped text
        self.table.resizeRowsToContents()

        self.returnHomeButton = QPushButton('Return Home')
        self.returnHomeButton.clicked.connect(self.on_return_home_clicked)

        topRightLayout = QHBoxLayout()
        topRightLayout.addStretch()
        topRightLayout.addWidget(self.returnHomeButton)

        mainLayout.addLayout(topRightLayout)

        # Layout for the add row buttons and label
        buttonLayout = QHBoxLayout()

        label = QLabel("Add Row:")
        buttonLayout.addWidget(label)

        self.addOneRowButton = QPushButton("+1")
        self.addOneRowButton.setFixedSize(40, 20)
        self.addOneRowButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.addOneRowButton.clicked.connect(lambda: self.add_new_rows(1))
        buttonLayout.addWidget(self.addOneRowButton)

        self.addFiveRowsButton = QPushButton("+5")
        self.addFiveRowsButton.setFixedSize(40, 20)
        self.addFiveRowsButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.addFiveRowsButton.clicked.connect(lambda: self.add_new_rows(5))
        buttonLayout.addWidget(self.addFiveRowsButton)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.table_context_menu)



        self.sortLabel = QLabel("Sort By:")
        buttonLayout.addWidget(self.sortLabel)

        self.sortComboBox = QComboBox(self)
        self.sortComboBox.addItem("Select a category")  # Adding a placeholder item

        self.sortComboBox.addItems(["Author", "Book Title", "Narrator", "Service"])
        self.sortComboBox.currentIndexChanged.connect(self.sort_table)  # Connect to the sorting function
        buttonLayout.addWidget(self.sortComboBox)

        # self.addColumnButton = QPushButton("Add Column", self)
        # self.addColumnButton.clicked.connect(self.add_column)
        # buttonLayout.addWidget(self.addColumnButton)
        #
        # self.renameColumnButton = QPushButton("Rename Column", self)
        # self.renameColumnButton.clicked.connect(self.rename_column)
        # buttonLayout.addWidget(self.renameColumnButton)




        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        buttonLayout.addSpacerItem(spacer)

        self.saveButton = QPushButton('Save Changes')
        self.saveButton.setStyleSheet("background-color: #ffff00;")  # Neon yellow color #F17B4A OLD

        self.saveButton.clicked.connect(self.save_changes_to_db)
        buttonLayout.addWidget(self.saveButton)

        mainLayout.addLayout(buttonLayout)
        mainLayout.addWidget(self.table)
        self.setLayout(mainLayout)

        searchLayout = QHBoxLayout()





        # Search by Title
        self.searchTitle = QLineEdit(self)
        self.searchTitle.setPlaceholderText("Search by Title")
        searchLayout.addWidget(self.searchTitle)

        # Search by Author
        self.searchAuthor = QLineEdit(self)
        self.searchAuthor.setPlaceholderText("Search by Author")
        searchLayout.addWidget(self.searchAuthor)

        # Search by Narrator
        self.searchNarrator = QLineEdit(self)
        self.searchNarrator.setPlaceholderText("Search by Narrator")
        searchLayout.addWidget(self.searchNarrator)

        # Search Button
        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.on_search_clicked)
        searchLayout.addWidget(self.searchButton)
        self.searchButton.clicked.connect(self.perform_search)

        mainLayout.addLayout(searchLayout)

        self.downloadButton = QPushButton('Download as Spreadsheet')
        self.downloadButton.clicked.connect(self.download_spreadsheet)
        mainLayout.addWidget(self.downloadButton)

    def column_resized(self, column, oldWidth, newWidth):
        self.save_column_widths()




    def save_changes_to_db(self):
        conn = sqlite3.connect('BooksDataFolder/books.db')
        cursor = conn.cursor()

        for row in range(self.table.rowCount()):
            # Check if the row has been changed
            title_item = self.table.item(row, 0)  # Assuming 0 is the column index for title
            author_item = self.table.item(row, 1)  # Assuming 1 is the column index for author
            if title_item and author_item and title_item.text().strip() and author_item.text().strip():
                if row in self.changed_rows:
                    # Fetch the item in the ID column
                    id_item = self.table.item(row, 0)
                    id_value = id_item.text() if id_item else None

                    # Prepare the values for all columns
                    values = [self.table.item(row, col).text() if self.table.item(row, col) else '' for col in
                              range(self.table.columnCount())]

                    if id_value and id_value.isdigit():
                        # Existing row - UPDATE
                        cursor.execute("""
                            UPDATE books SET 
                            title=?, author=?, "Memorable Characters"=?, audible=?, narrator=?, 
                            "Best Quotes"=?, "Memorable Content"=?, recommend=?, service=?
                            WHERE id=?
                        """, values + [id_value])
                    else:
                        # New row - INSERT
                        cursor.execute("""
                            INSERT INTO books (
                                title, author, "Memorable Characters", audible, narrator, 
                                "Best Quotes", "Memorable Content", recommend, service
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, values[1:])  # Assuming first value is ID and should be skipped

        conn.commit()
        conn.close()
        self.changed_rows.clear()  # Clear the set of changed rows
        self.load_data_from_db()  # Reload data to reflect the changes in the UI

    def add_new_rows(self, number_of_rows):
        currentRowCount = self.table.rowCount()
        self.table.setRowCount(currentRowCount + number_of_rows)
        for i in range(number_of_rows):
            for j in range(self.table.columnCount()):
                self.table.setItem(currentRowCount + i, j, QTableWidgetItem(''))

    def track_change(self, item):
        if self.is_loading_data:
            # Ignore changes that are happening because data is being loaded from the DB
            return

        # Record the row number of the changed item.
        self.changed_rows.add(item.row())

    def save_changes_to_db(self):
        conn = sqlite3.connect('BooksDataFolder/books.db')
        cursor = conn.cursor()

        for row in self.changed_rows:
            row_id = self.row_id_map.get(row)
            values = [self.table.item(row, col).text() if self.table.item(row, col) else '' for col in
                      range(self.table.columnCount())]

            if row_id:
                # Existing row - UPDATE
                cursor.execute("""
                    UPDATE books SET 
                    title=?, author=?, "Memorable Characters"=?, audible=?, narrator=?, 
                    "Best Quotes"=?, "Memorable Content"=?, recommend=?, service=?
                    WHERE id=?
                """, values + [str(row_id)])
            else:
                # New row - INSERT
                cursor.execute("""
                    INSERT INTO books (
                        title, author, "Memorable Characters", audible, narrator, 
                        "Best Quotes", "Memorable Content", recommend, service
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values)

        conn.commit()
        conn.close()
        self.changed_rows.clear()
        self.load_data_from_db()

    # def add_column_to_db(self, column_name):
    #     conn = sqlite3.connect('books.db')
    #     cursor = conn.cursor()
    #     cursor.execute(f"ALTER TABLE books ADD COLUMN {column_name} TEXT")
    #     conn.commit()
    #     conn.close()
    #
    # def rename_column_in_db(self, old_column_name, new_column_name):
    #     conn = sqlite3.connect('books.db')
    #     cursor = conn.cursor()
    #
    #     cursor.execute(f"ALTER TABLE books RENAME COLUMN {old_column_name} TO {new_column_name}")
    #     conn.commit()
    #     conn.close()
    #
    # def add_column(self):
    #     column_name, ok = QInputDialog.getText(self, "Add Column", "Enter the name of the new column:")
    #     if ok and column_name:
    #         self.add_column_to_db(column_name)
    #         self.table.insertColumn(self.table.columnCount())
    #         self.table.setHorizontalHeaderLabels(self.get_all_column_names_from_db())
    #
    # def rename_column(self):
    #     old_column_name, ok = QInputDialog.getItem(self, "Rename Column", "Select a column:",
    #                                                self.get_all_column_names_from_db())
    #     if ok and old_column_name:
    #         new_column_name, ok = QInputDialog.getText(self, "Rename Column", "Enter the new name for the column:")
    #         if ok and new_column_name:
    #             self.rename_column_in_db(old_column_name, new_column_name)
    #             self.load_data_from_db()  # Refresh the table to reflect changes
    #
    # def get_all_column_names_from_db(self):
    #     conn = sqlite3.connect('books.db')
    #     cursor = conn.cursor()
    #     cursor.execute("PRAGMA table_info(books)")
    #     columns = [info[1] for info in cursor.fetchall()]  # index 1 is the column name
    #     conn.close()
    #     return columns[1:]



    def track_change(self, item):
        if not self.is_loading_data:
            self.changed_rows.add(item.row())

    def prompt_save_changes(self):
        if self.changed_rows:
            reply = QMessageBox.question(self, 'Save Changes',
                                         "You have unsaved changes. Would you like to save them before exiting?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                self.save_changes_to_db()



    def on_return_home_clicked(self):
        self.prompt_save_changes()
        self.main_window.show_home_page()


    def get_column_name_by_index(self, index):
        columns = ["id", "title", "author", "characters", "audible", "narrator", "quotes", "content", "recommend", "service"]
        return columns[index]

    def on_search_clicked(self):
        title = self.searchTitle.text()
        author = self.searchAuthor.text()
        narrator = self.searchNarrator.text()
        self.load_data_from_db(title, author, narrator)

    def load_data_from_db(self):
        self.is_loading_data = True
        self.row_id_map.clear()  # Clear existing ID map

        conn = sqlite3.connect('BooksDataFolder/books.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, title, author, "Memorable Characters", audible, narrator, "Best Quotes", "Memorable Content", recommend, service FROM books')
        books = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(books))
        for row_idx, book in enumerate(books[1:]):
            self.row_id_map[row_idx] = book[0]  # Store the row's ID
            for col_idx, data in enumerate(book[1:]):
                data = "" if data is None or data == "None" else str(data)
                item = CaseInsensitiveTableWidgetItem(data)
                self.table.setItem(row_idx, col_idx, item)

        self.table.resizeRowsToContents()
        self.is_loading_data = False

    def sort_table(self, index):
        if index == 0:  # Placeholder item is at index 0
            return
        column_mapping = {
            "Book Title": 0,  # "Book Title" corresponds to the first column
            "Author": 1,      # "Author" to the second column
            "Narrator": 4,    # "Narrator"
            "Service": 8      # "Service"
        }

        column_to_sort = column_mapping.get(self.sortComboBox.currentText(), 0)  # Default to sorting by "Book Title"
        self.table.setSortingEnabled(False)  # Disable sorting while making changes

        # Set the custom sorting item
        for row in range(self.table.rowCount()):
            item = self.table.item(row, column_to_sort)
            if item:
                self.table.setItem(row, column_to_sort, CaseInsensitiveTableWidgetItem(item.text()))

        self.table.setSortingEnabled(True)  # Re-enable sorting
        self.table.sortItems(column_to_sort, Qt.AscendingOrder)  # Sort the table

    def perform_search(self):
        # Get the text from the QLineEdit widgets
        title_search = self.searchTitle.text().lower().strip()
        author_search = self.searchAuthor.text().lower().strip()
        narrator_search = self.searchNarrator.text().lower().strip()

        # Flags to check if we have search criteria for each category
        search_for_title = bool(title_search)
        search_for_author = bool(author_search)
        search_for_narrator = bool(narrator_search)

        # Iterate over the rows of the table to find a match
        for row in range(self.table.rowCount()):
            # Initial assumption is that we have a match
            title_matches = not search_for_title
            author_matches = not search_for_author
            narrator_matches = not search_for_narrator

            # If we are searching for a title, check the current row for a match
            if search_for_title:
                title_item = self.table.item(row, 0)  # Adjust the column index if needed
                title_matches = title_item and title_search in title_item.text().lower()

            # If we are searching for an author, check the current row for a match
            if search_for_author:
                author_item = self.table.item(row, 1)  # Adjust the column index if needed
                author_matches = author_item and author_search in author_item.text().lower()

            # If we are searching for a narrator, check the current row for a match
            if search_for_narrator:
                narrator_item = self.table.item(row, 4)  # Adjust the column index if needed
                narrator_matches = narrator_item and narrator_search in narrator_item.text().lower()

            # If all specified criteria match, select the row and exit the search
            if title_matches and author_matches and narrator_matches:
                self.table.selectRow(row)
                self.table.scrollToItem(self.table.item(row, 0))
                break  # Comment out this line if you want to continue searching for additional matches

    def download_spreadsheet(self):
        try:
            # Get the path to the user's Downloads folder
            downloads_path = str(Path.home() / 'Downloads')
            output_path = os.path.join(downloads_path, 'exported_books.xlsx')

            export_database_to_spreadsheet(output_path=output_path)

            QMessageBox.information(self, "Download Complete",
                                    f"Spreadsheet downloaded successfully to {output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def table_context_menu(self, position):
        menu = QMenu(self.table)

        # Add actions for inserting rows
        insert_above_action = menu.addAction("Insert Row Above")
        insert_below_action = menu.addAction("Insert Row Below")

        action = menu.exec_(self.table.viewport().mapToGlobal(position))

        if action == insert_above_action:
            self.insert_row_above()
        elif action == insert_below_action:
            self.insert_row_below()

    def insert_row_above(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.insertRow(current_row)

    def insert_row_below(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.insertRow(current_row + 1)

    def save_column_widths(self):
        with open(self.column_widths_file, 'w') as file:
            for column in range(self.table.columnCount()):
                width = self.table.columnWidth(column)
                file.write(str(width) + '\n')

    def load_column_widths(self):
        try:
            with open(self.column_widths_file, 'r') as file:
                widths = file.readlines()
                for column, width in enumerate(widths):
                    self.table.setColumnWidth(column, int(width.strip()))
        except FileNotFoundError:
            # File not found, set default widths
            self.set_default_column_widths()

    def set_default_column_widths(self):
        default_widths = [135, 100, 127, 65, 120, 300, 340, 90, 120]

        # Check if the file exists
        if not os.path.exists(self.column_widths_file):
            with open(self.column_widths_file, 'w') as file:
                for width in default_widths:
                    file.write(str(width) + '\n')

        # Now set the column widths from the file
        self.load_column_widths()