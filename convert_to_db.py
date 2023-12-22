# ONLY EDIT THE PATH OF YOUR SPREADSHEET WHEN CHANGING THIS FILE #
# To download your spreadsheet, go to sheets / excel / your program #
# Go to File, Download, Download as '.xlsx' #
# Right click file that pops up and click 'Show in Folder', or go to recent downloads #
# Right click, and press 'copy as file' #
# Enter file name at the bottom of this page where it says 'excel path' #




import pandas as pd
import sqlite3


# Step 1: Read the data from the spreadsheet
def read_spreadsheet(excel_path):
    df = pd.read_excel(excel_path, engine='openpyxl')
    # Remove 'id' column if present
    df = df.drop(columns=['id'], errors='ignore')
    return df


# Step 2: Write the DataFrame to a SQLite database
def write_to_database(df, db_path='books.db'):
    conn = sqlite3.connect(db_path)
    # Ensure there's no 'id' column in the DataFrame
    df.to_sql('books', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()


# ENTER FILE NAME BELOW as, excel_path = "Placeholder_path" #
# WINDOWS USERS >>> PLEASE CHANGE '\' to '/' OR IT WON'T WORK #

excel_path = "C:/Users/Steve/Downloads/finished_spreadsheet.xlsx"  # Change this to the path of your spreadsheet
df = read_spreadsheet(excel_path)
write_to_database(df)
