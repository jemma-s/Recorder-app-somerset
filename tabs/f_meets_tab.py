"""
TAB 6
Tab for downloading swim meet results
"""
import pandas as pd
import calendar
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QFileDialog,QMessageBox)
from PyQt6.QtCore import Qt
from datetime import date
from datetime import datetime
from Pool_meets_functions import *


class MeetsTab(QWidget):
    """Tab for downloading meet results"""
    
    def __init__(self, data_store):
        super().__init__()
        self.data_store = data_store
        self.init_ui()
        self.meets_store = None
        self.results_store = None
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Downloading pool meets data")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Instructions
        info = QLabel("This gets meet data directly from the MSA website (https://portal.msarc.org.au/results/results.php?js=on)")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        # Year selection
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Select a year:"))
        self.year_combo = QComboBox()
        self.year_combo.addItems(['2022', '2023', '2024', '2025', '2026', '2027', '2028'])
        self.year_combo.setCurrentText('2025')
        year_layout.addWidget(self.year_combo)
        year_layout.addStretch()
        layout.addLayout(year_layout)
        
        # Load meets button
        self.load_meets_btn = QPushButton("🏊‍♀️ Load the swim meets for the year selected")
        self.load_meets_btn.clicked.connect(self.load_meets)
        #self.load_meets_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.load_meets_btn)
        layout.addStretch()
        
        # Meets table
        self.meets_table = QTableWidget()
        self.meets_table.setVisible(False)
        layout.addWidget(self.meets_table)
        #layout.addSpacing(50)

        self.results_combobox = QComboBox() #text: "What do you want to find?"
        self.results_combobox.addItems(["Results of a certain meet",
                                        "Results of a certain swimmer for the year", 
                                        "All results in the year",
                                        "Combined year results - For awards"])
        self.results_combobox.currentTextChanged.connect(self.meets_swimmer_selector)
        self.results_combobox.setVisible(False)
        layout.addWidget(self.results_combobox)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.meets_swimmer_combobox = QComboBox() #text: "Select an option"
        #self.meets_swimmer_combobox.addItems(self.meets_swimmer_selector)
        self.meets_swimmer_combobox.setVisible(False)
        layout.addWidget(self.meets_swimmer_combobox)
        layout.addStretch()

        self.load_results_btn = QPushButton("👆 Find the results")
        self.load_results_btn.clicked.connect(self.load_results)
        self.load_results_btn.setVisible(False)
        layout.addWidget(self.load_results_btn)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setVisible(False)
        layout.addWidget(self.results_table)
        layout.addSpacing(50)

        # Download button
        layout.addSpacing(50)
        self.download_btn = QPushButton("📥 Download results excel")
        self.download_btn.clicked.connect(self.download_results)
        self.download_btn.setVisible(False)
        #self.download_btn.setStyleSheet(self._get_download_button_style())
        layout.addWidget(self.download_btn)
        

    def load_meets(self):
        self.load_meets_btn.setEnabled(False)

        year = self.year_combo.currentText()

        df = meets_list_from_url(year)
        del df['URL'] # Removing the 'URL'column
        self.meets_store = df
        self.results_combobox.setVisible(True)
        #self.display_meets_table(df)
    
    
    def display_meets_table(self, df):
        """Display members data in table"""
        self.meets_table.setVisible(True)
        self.meets_table.setRowCount(len(df))
        self.meets_table.setColumnCount(len(df.columns))
        self.meets_table.setHorizontalHeaderLabels(df.columns)
        
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                item = QTableWidgetItem(str(df.iloc[i, j]))
                self.meets_table.setItem(i, j, item)
        
        self.meets_table.resizeColumnsToContents()
        header = self.meets_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def display_results_table(self, df):
        """Display results data in table"""
        self.results_table.setVisible(True)
        self.results_table.setRowCount(len(df))
        self.results_table.setColumnCount(len(df.columns))
        self.results_table.setHorizontalHeaderLabels(df.columns)
        
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                item = QTableWidgetItem(str(df.iloc[i, j]))
                self.results_table.setItem(i, j, item)
        
        self.results_table.resizeColumnsToContents()
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def meets_swimmer_selector(self):
        """" Output either a list of swimmers as (stored in store data) or a list of meets to choose """

        selected_result_combobox = self.results_combobox.currentText()
        self.meets_swimmer_combobox.clear()
        self.load_results_btn.setVisible(True)

        if selected_result_combobox == "Results of a certain swimmer for the year":
            if not self.data_store.has_members_data():
                self.show_no_data_message()
                self.meets_swimmer_combobox.setVisible(False)
                return
            else:
                memberslist = self.data_store.members_df.copy()
                memberslist = memberslist["Full name"]
                self.meets_swimmer_combobox.addItems(memberslist.tolist())
                self.meets_swimmer_combobox.setVisible(True)
                self.status_label.setText("Select a swimmer")
        elif selected_result_combobox == "Results of a certain meet":
            meetslist = self.meets_store
            meetslist = meetslist['Meet']
            self.meets_swimmer_combobox.addItems(meetslist.tolist())
            self.meets_swimmer_combobox.setVisible(True)
            self.status_label.setText("Select a swim meet")
        else:
            self.meets_swimmer_combobox.setVisible(False)
            self.status_label.setText("")
            return
        

    def show_no_data_message(self):
        """Show message when no data is available"""
        self.load_results_btn.setVisible(False)
        self.status_label.setText("⚠️ No member data loaded. Please upload members file in the 'Upload Members Data' tab first.")
        self.status_label.setStyleSheet("color: orange; font-weight: bold; font-size: 14px;")

    def load_results(self):
        """Loading results for the selected meet/swimmer for the selected option"""
        selected_result_combobox = self.results_combobox.currentText()
        selected_meets_swimmer_combobox = self.meets_swimmer_combobox.currentText()
        year = self.year_combo.currentText()

        if selected_result_combobox == "Results of a certain swimmer for the year":
            # First we need to find the selected swimmer's MSWA number in the stored df
            memberslist = self.data_store.members_df.copy()
            MSWA_number = memberslist.loc[memberslist["Full name"] == selected_meets_swimmer_combobox, "MSWA number"].values.item()
            firstname = memberslist.loc[memberslist["Full name"] == selected_meets_swimmer_combobox, "First name"].values.item()
            surname = memberslist.loc[memberslist["Full name"] == selected_meets_swimmer_combobox, "Surname"].values.item()

            df = individual_swimmers_results(MSWA_number, year, firstname, surname)
            print(df)
        
        elif selected_result_combobox == "All results in the year":
            memberslist = self.data_store.members_df.copy()
            df = all_swimmers_results(memberslist, year)

        elif selected_result_combobox == "Combined year results - For awards":
            memberslist = self.data_store.members_df.copy()
            df = all_swimmers_results_grouped_points(memberslist, year)

        if df is not None:
            self.results_store = df
            self.display_results_table(df)
            self.download_btn.setVisible(True)

    
    def download_results(self):
        """Download results to Excel"""
        if self.results_store is None:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "Swim-meet-results.xlsx", "Excel Files (*.xlsx)")
        
        if file_path:
            try:
                self.results_store.to_excel(file_path, index=False)
                QMessageBox.information(self, "Success", "Results saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")


    
