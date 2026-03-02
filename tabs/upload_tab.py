"""
TAB 1
Tab for uploading member data into the app
"""
import pandas as pd
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QComboBox, QProgressBar,
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QHeaderView, QTextEdit)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

# Import scraper functions
from EM1000_functions import setup_driver, input_swimmer_search, extract_swimmer_data
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

        info2 = QLabel("Before proceeding, download the members report from Swim Central - or ask someone with access to send it to you")
        info2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info2)
        
        # Upload button
        self.upload_btn = QPushButton("📁 Upload members file (excel or csv)")
        self.upload_btn.clicked.connect(self.upload_members_file)
        self.upload_btn.setStyleSheet(self._get_upload_button_style())
        self.upload_btn.setMinimumHeight(60)
        layout.addWidget(self.upload_btn)
        
        # Upload instructions
        layout.addWidget(QLabel("Note: Make sure the file is in the following format"))
        layout.addWidget(QLabel("First name | Surname | DOB | Gender | Account status | Add date | Membership type | MSWA Number | Club"))
        #layout.addSpacing(10)
        
        # File status
        self.file_status = QLabel("")
        layout.addWidget(self.file_status)
        
        # Members table
        self.members_table = QTableWidget()
        self.members_table.setVisible(False)
        self.members_table.setMaximumHeight(300)
        layout.addWidget(self.members_table)
        layout.addSpacing(50)
        
    
    def upload_members_file(self):
        """Upload members file (CSV or Excel)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Members File", "", 
            "All Supported Files (*.xlsx *.xls *.csv);;Excel Files (*.xlsx *.xls);;CSV Files (*.csv)")
        
        if file_path:
            #column_names = ["First name", "Surname", "DOB", "Gender", "Status", 
            #  
            column_names = ["First name", "Surname", 
                            "Age", "DOB", 
                            "Gender", "MSWA number"] 
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
                df["DOB"] = pd.to_datetime(df["DOB"], format='%d/%m/%Y')
                df["Full name"] = df["First name"].str.cat(df["Surname"], sep=" ")
                
                if "Status" in df.columns:
                    df = df[df.Status != "Terminated"]
                
                # Note to future Jemma - add error checking here. If there's an error, there's an ID number missing from the CSV
                df["MSWA number"] = df['MSWA number'].astype(int)
                
                self.data_store.set_members_data(df)
                self.display_members_table(df)
                
                self.file_status.setText(f"✓ Loaded {len(df)} active members from {file_path.split('/')[-1]}")
                self.file_status.setStyleSheet("color: green; font-weight: bold;")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}\n\nPlease ensure the file contains a 'MSWA number' column.")


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
                value = df.iloc[i, j]  # ✨ NEW: Store the value first
            
                # ✨ NEW: Check if column is a date type and format it
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    if pd.notna(value):
                        item = QTableWidgetItem(value.strftime('%d/%m/%Y'))
                    else:
                        item = QTableWidgetItem('')
                else:
                    item = QTableWidgetItem(str(value))  # Original behavior
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
    