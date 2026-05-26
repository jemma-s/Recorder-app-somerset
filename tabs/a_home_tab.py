"""
TAB 1
Tab for explaining how to use the app
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

class HomeTab(QWidget):
    # To explain how to use the app

    def __init__(self, data_store):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Welcome to the Somerset Masters recording app!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Instructions
        info = QLabel("How to use")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        info1 = QLabel("This app can be used to get results from swim meets or the endurance 1000 (E1000) competition")
        info1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(info1)

        tabb = QLabel(f"<b>🦭 Upload Members</b> <br> Where you can upload an excel document with a list of current Somerset Members. This list is then used on other pages of the app. ")
        tabb.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(tabb)

        tabc = QLabel(f"<b>🎂 Birthdays</b> <br> Uses the list of members uploaded in '🦭 Upload Members' and gives a list of birthdays for each month. This is used for producing the monthly newsletter.")
        tabc.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(tabc)

        tabd = QLabel(f"<b>📥 Get E1000 Data</b> <br> Uses the list of members uploaded in '🦭 Upload Members' and will find the current E1000 results on the MSA website. Creates an excel document with a list of each swim.")
        tabd.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(tabd)

        tabe = QLabel(f"<b>📊 Visualise E1000 Data</b> <br> Requires you to upload the excel document saved after getting E1000 data from '📥 E1000 Results' or '🎣 Other Club E1000 Results'. Gives a quick insight into the data.")
        tabe.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(tabe)

        tabf = QLabel(f"<b>🏎️ Get Swim Meet Results</b> <br> Uses the list of members uploaded in '🦭 Upload Members' to find swim meet results for the whole year or for a specific swimmer. ")
        tabf.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(tabf)

        tabg = QLabel(f"<b>🪼 Find members - for other clubs</b> <br> Finds a list of swimmers who have completed an endurance swim from a selected club. ")
        tabg.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(tabg)

        tabh = QLabel(f"<b>🎣 Get E1000 results - for other clubs</b> <br> Uses the list of swimmers generated after using '🪼 Other Club Members'. Will find the current E1000 results on the MSA website. Creates an excel document with a list of each swim.")
        tabh.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(tabh)
        
