"""
TAB 2
Tab for uploading member data into the app
"""
import pandas as pd
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QComboBox, QProgressBar,
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QHeaderView, QTextEdit)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

# Import scraper functions
from functions.EM1000_functions import setup_driver, input_swimmer_search, extract_swimmer_data
import time


class UploadTab(QWidget):
    """Tab for initially uploading member data into the app"""
    
    def __init__(self, data_store):
        super().__init__()
        self.data_store = data_store
        self.scraper_thread = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Upload the members data file")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

        info2 = QLabel("Before proceeding, download the members report from Swim Central (or ask someone with access to send it to you)")
        info2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info2)

        # Upload instructions
        layout.addWidget(QLabel("Note: Make sure the file is in the following format"))
        layout.addWidget(QLabel("First name | Surname | DOB | Gender | Status | MSWA number"))
        layout.addWidget(QLabel("* DOB is in format 'Date/Month/Year (e.g. 30/04/1990)"))
        layout.addWidget(QLabel("* Gender is either 'Male' or 'Female'"))
        layout.addWidget(QLabel("* Status is either 'Active' or 'Terminated'"))
        #layout.addSpacing(10)
        
        # Upload button
        self.upload_btn = QPushButton("📁 Upload members file (Excel or Csv)")
        self.upload_btn.clicked.connect(self.upload_members_file)
        self.upload_btn.setStyleSheet(self._get_upload_button_style())
        self.upload_btn.setMinimumHeight(60)
        layout.addWidget(self.upload_btn)
        
        # File status
        self.file_status = QLabel("")
        layout.addWidget(self.file_status)
        
        # Members table
        self.members_table = QTableWidget()
        self.members_table.setVisible(False)
        self.members_table.setMaximumHeight(300)
        layout.addWidget(self.members_table)
        layout.addSpacing(50)

        # Adding sentence to prompt user to either download data or to access birthdays
        self.user_status = QLabel("")
        layout.addWidget(self.user_status)
        
    
    def upload_members_file(self):
        """Upload members file (CSV or Excel)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Members File", "", 
            "All Supported Files (*.xlsx *.xls *.csv);;Excel Files (*.xlsx *.xls);;CSV Files (*.csv)")
        
        if file_path:
            column_names = ["First name", "Surname", 
                            "DOB", "Gender",
                            "Status", 
                            "MSWA number"] 
            # Initial read-in
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path,
                                     header = None, 
                                     skiprows = 1)
                else:
                    df = pd.read_excel(file_path, 
                                       header = None, 
                                       skiprows = 1)

                df.columns = column_names
                df["Full name"] = df["First name"].str.cat(df["Surname"], sep=" ")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"There was an error reading the file: {str(e)}. Check that it is in the correct format. ")
                return
            
            # Converting DOB to date format
            try:
                df["DOB"] = pd.to_datetime(df["DOB"], format='%d/%m/%Y')
            except Exception as e:
                QMessageBox.critical(self, "Error", "The DOB column is in the incorrect format. Please ensure dates are in DD/MM/YYYY format.")
                return
            
            # Filtering for terminated members
            try:
                if "Status" in df.columns:
                    df = df[df.Status != "Terminated"]
            except Exception as e:
                QMessageBox.critical(self, "Error", "The Status column is not correct. Please ensure status contains either 'Active' or 'Terminated'.")
                return
            
            # Converting MSWA numbers to numbers
            try:
                df["MSWA number"] = df['MSWA number'].astype(int)
            except Exception as e:
                QMessageBox.critical(self, "Error", "Theres an error with MSWA numbers. Please ensure every member has a number")
                return
            
            # Creating the members table
            try:
                
                self.data_store.set_members_data(df)
                self.display_members_table(df)
                
                self.file_status.setText(f"✓ Loaded {len(df)} active members from {file_path.split('/')[-1]}")
                self.file_status.setStyleSheet("color: green; font-weight: bold;")
                self.user_status.setText("Somerset members has now been loaded! Now, either go to the '🎂 Birthdays' tab or the '📥 E1000 Results' tab or the '🏎️ Swim Meets Results' tab.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}\n\nError when creating table")


    def display_members_table(self, df):
        """Display members data in table widget."""
        if df is None or len(df) == 0:
            return
        
        self.members_table.setVisible(True)
        self.members_table.setRowCount(len(df))  
        self.members_table.setColumnCount(len(df.columns))
        self.members_table.setHorizontalHeaderLabels(df.columns)
        
        for i in range(min(len(df), len(df))):
            for j, col in enumerate(df.columns):
                value = df.iloc[i, j]  
            
                # Formatting date column
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    if pd.notna(value):
                        item = QTableWidgetItem(value.strftime('%d/%m/%Y'))
                    else:
                        item = QTableWidgetItem('')
                else:
                    item = QTableWidgetItem(str(value))  
                self.members_table.setItem(i, j, item)
        
        self.members_table.resizeColumnsToContents()
        header = self.members_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
  
    def _get_upload_button_style(self):
        return """
            QPushButton {
                background-color: #f0f0f0;
                border: 2px dashed #999;
                border-radius: 8px;
                padding: 20px;
                font-size: 14px;
                color: #333;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
                border-color: #1E40AF;
                color: #1E40AF;
            }
            QPushButton:pressed {
                background-color: #d8d8d8;
            }
        """
    