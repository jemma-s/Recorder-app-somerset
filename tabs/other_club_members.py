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
        self.club_members = None
    
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

        # Drop down club select
        self.club_select_info = QLabel("Select a club that you want to find the swimmers of")
        self.club_select_info_2 = QLabel("You can find a PDF list of clubs and codes HERE: https://mastersswimming.org.au/about/states-territory-and-affiliated-clubs/")
        self.club_select_info.setVisible(False) # Becomes visible after the swimmers have been loaded in and year selected
        layout.addWidget(self.club_select_info)
        self.club_select_info_2.setVisible(False) # Becomes visible after the swimmers have been loaded in and year selected
        layout.addWidget(self.club_select_info_2)

        self.club_select = QComboBox()
        self.club_select.setVisible(False) # Becomes visible after the swimmers have been loaded in and year selected
        self.club_select.currentIndexChanged.connect(self.display_swimmers_table)
        layout.addWidget(self.club_select)
        layout.addSpacing(50)
        
        # Swimmers table
        self.swimmers_table = QTableWidget()
        self.swimmers_table.setVisible(False)
        layout.addWidget(self.swimmers_table)
        #layout.addSpacing(50)




     
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
            #url = "https://portal.msarc.org.au/meets/index.php?EventId=154524&filter=*&split=no&scope=&js=on"
            url = "https://portal.msarc.org.au/meets/index.php?EventId=154524"
        else:
            # This will need to be improved: either the user can copy and paste the URL in or....?
            url = "TBA"

        data = requests.get(url).text
        soup = BeautifulSoup(data, 'html.parser') #Getting the HTML
        #print(soup)
        rows = []

        for tr in soup.find_all("tr"):
            cells = tr.find_all("td", class_="result")
            if len(cells) >4: # Will stop the loop if it's an empty list
                name = cells[1].get_text(strip=True)
                age  = cells[2].get_text(strip=True)
                club = cells[3].get_text(strip=True)
                id_  = cells[4].get_text(strip=True)
                rows.append({"Name": name, "Age": age, "Club": club, "ID": id_})

        df = pd.DataFrame.from_dict(rows)
        df = df.drop_duplicates() #removing duplicates as we only need single instances
        #print(df)
        self.club_members = df #Storing the df for later use
        self.data_store.set_results_selected_members_other_club_df(df)

        # Finding list of unique clubs for drop down
        unique_clubs = sorted(df['Club'].unique())
        self.club_select.addItems(unique_clubs)
        self.club_select.setVisible(True)

        self.club_select_info.setVisible(True) # Becomes visible after the swimmers have been loaded in and year selected
        self.club_select_info_2.setVisible(True) # Becomes visible after the swimmers have been loaded in and year selected
    

    
    
    def display_swimmers_table(self, df):
        """Display members data in table once a year and club is selected"""
        df = self.club_members
        selected_club = self.club_select.currentText()
        df__selected = df[df['Club'] == selected_club]
        self.data_store.set_selected_club(selected_club)
        self.swimmers_table.setVisible(True)
        self.swimmers_table.setRowCount(len(df__selected))
        self.swimmers_table.setColumnCount(len(df__selected.columns))
        self.swimmers_table.setHorizontalHeaderLabels(df__selected.columns)
        
        for i in range(len(df__selected)):
            for j, col in enumerate(df__selected.columns):
                item = QTableWidgetItem(str(df__selected.iloc[i, j]))
                self.swimmers_table.setItem(i, j, item)
        
        self.swimmers_table.resizeColumnsToContents()
        header = self.swimmers_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        

        



  


    