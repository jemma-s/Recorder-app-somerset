"""
TAB ?
Tab for finding swimmers from other clubs who have competed in endurance swims this year
"""

"""
TAB 6
Tab for downloading swim meet results
"""

# 2025 Endurance log - https://portal.msarc.org.au/meets/index.php?EventId=154331&filter=*&split=no&scope=&js=on
# 2026 Endurance log - https://portal.msarc.org.au/meets/index.php?EventId=154524&filter=*&split=no&scope=&js=on
# Note that this will change for future years, may need to let the user edit it
# Note that the logs may not include all the current results
# The main purpose of this page is to create a database of current swimmers and their ID numbers, so their endurance results and points can be found

import pandas as pd
import calendar
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QFileDialog,QMessageBox)
from PyQt6.QtCore import Qt
from datetime import date
from datetime import datetime
from Pool_meets_functions import *


class Other_Club_Members(QWidget):
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
        title = QLabel("Finding current endurance swimmers from other clubs")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Instructions
        info = QLabel("This will find a list of swimmers who have logged a swim on the MSWA website (https://portal.msarc.org.au/results/results.php?js=on)")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        info2 = QLabel("Note: the MSWA website results doesn't update instantly. This means the list of swimmers should just be used as a guide")
        info2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info2)
        
        # Year selection
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Select a year:"))
        self.year_combo = QComboBox()
        self.year_combo.addItems(['2025', '2026', 'Other'])
        self.year_combo.setCurrentText('2026')
        year_layout.addWidget(self.year_combo)
        year_layout.addStretch()
        layout.addLayout(year_layout)
        
        # Load meets button
        self.load_meets_btn = QPushButton("🏊‍♀️ Load the swimmers from the year selected")
        self.load_meets_btn.clicked.connect(self.load_meets)
        #self.load_meets_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.load_meets_btn)
        layout.addStretch()
        
        # Swimmers table
        self.swimmers_table = QTableWidget()
        self.swimmers_table.setVisible(False)
        layout.addWidget(self.swimmers_table)
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


     
# 2025 Endurance log - https://portal.msarc.org.au/meets/index.php?EventId=154331&filter=*&split=no&scope=&js=on
# 2026 Endurance log - https://portal.msarc.org.au/meets/index.php?EventId=154524&filter=*&split=no&scope=&js=on
#   

    def load_meets(self):
        # This is actioned after the button is clicked to find swimmers
        self.load_meets_btn.setEnabled(False)

        # Linking the year selected to the url needed
        year = self.year_combo.currentText()
        if year == "2025":
            url = "https://portal.msarc.org.au/meets/index.php?EventId=154331&filter=*&split=no&scope=&js=on"
        elif year == "2026":
            url = "https://portal.msarc.org.au/meets/index.php?EventId=154524&filter=*&split=no&scope=&js=on"
        else:
            # This will need to be improved: either the user can copy and paste the URL in or....?
            url = "TBA"

        data = requests.get(url).text
        soup = BeautifulSoup(data, 'html.parser') #Getting the HTML

        print(soup)


        #self.meets_store = df
        #self.results_combobox.setVisible(True)
        #self.display_swimmers_table(df)
    
    
    def display_swimmers_table(self, df):
        """Display members data in table"""
        self.swimmers_table.setVisible(True)
        self.swimmers_table.setRowCount(len(df))
        self.swimmers_table.setColumnCount(len(df.columns))
        self.swimmers_table.setHorizontalHeaderLabels(df.columns)
        
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                item = QTableWidgetItem(str(df.iloc[i, j]))
                self.swimmers_table.setItem(i, j, item)
        
        self.swimmers_table.resizeColumnsToContents()
        header = self.swimmers_table.horizontalHeader()
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


    