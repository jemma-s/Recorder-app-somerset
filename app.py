#Main application entry point for E1000 PyQt6 App
#Note for my computer: uses virtual environment somerset_venv
#somerset_venv\Scripts\activate *** do this in powershell
#deactivate

import sys
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

# Import tab modules
from tabs.b_upload_tab import UploadTab
from tabs.d_scrape_tab import ScrapeTab
from tabs.e_visualize_tab import VisualizeTab
from tabs.c_birthday_tab import BirthdayTab
from tabs.f_meets_tab import MeetsTab
from tabs.g_other_club_members import Other_Club_Members
from tabs.h_scrape_other_club_members import ScrapeTabOtherClubSelected

# Import shared data store
from shared_data import DataStore


class E1000App(QMainWindow):
    """Main application window with tabbed interface"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Somerset Masters Swimming - E1000")
        self.setGeometry(100, 100, 1600, 900)
        
        # Initialize shared data store
        self.data_store = DataStore()
        
        # Load Somerset points reference data
        #try:
        #    self.data_store.e1000_sheet = pd.read_excel(
        #        "C:/Users/Arinda/Documents/Somerset/Downloading MSA Results/Data Files/Somerset_points.xlsx"
        #    )
        #except:
        #    print("Warning: Could not load Somerset_points.xlsx")
        #    self.data_store.e1000_sheet = None
        
        # Setup UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""


        self.scroll = QScrollArea()

        central_widget = QWidget()
        #self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Create tab instances (passing data_store to each)
        self.upload_tab = UploadTab(self.data_store)
        self.scrape_tab = ScrapeTab(self.data_store)
        self.visualize_tab = VisualizeTab(self.data_store)
        self.birthday_tab = BirthdayTab(self.data_store)
        self.meets_tab = MeetsTab(self.data_store)
        self.other_club_members_tab = Other_Club_Members(self.data_store)
        self.scrape_other_members_tab = ScrapeTabOtherClubSelected(self.data_store)
        
        # Add tabs to widget
        self.tabs.addTab(self.upload_tab, "🦭 Upload Members Data")
        self.tabs.addTab(self.birthday_tab, "🎂 Birthday Calendar")
        self.tabs.addTab(self.scrape_tab, "📥 Get E1000 Data")
        self.tabs.addTab(self.visualize_tab, "📊 Visualize E1000 Data")
        self.tabs.addTab(self.meets_tab, "🏎️ Get Swim Meets Results")
        self.tabs.addTab(self.other_club_members_tab, "🪼 Find members - for other clubs")
        self.tabs.addTab(self.scrape_other_members_tab, "🎣 Get E1000 results - for other clubs")

        
        # Connect tab change signal to update tabs
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        main_layout.addWidget(self.tabs)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollBar:vertical { width: 20px; }")
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(central_widget)
        self.setCentralWidget(self.scroll)
        self.setGeometry(600, 100, 1000, 1800) #x coordinate at top left, y coordinate at top left, width, height
    
    def create_header(self):
        """Create header with logo and title"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        # Left: EM 1000
        left_label = QLabel("E1000")
        left_label.setStyleSheet("font-size: 16px;")
        header_layout.addWidget(left_label)
        
        # Center: Title
        title_label = QLabel("Somerset Masters Swimming Club")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label, stretch=2)
        
        # Right: Logo (if exists)
        try:
            logo_label = QLabel()
            pixmap = QPixmap("assets/somerset_logo.jpg")
            logo_label.setPixmap(pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
            header_layout.addWidget(logo_label)
        except:
            header_layout.addWidget(QLabel(""))  # Placeholder
        
        header_widget.setStyleSheet("border-bottom: 1px solid #ccc; padding: 10px;")
        return header_widget
    
    def on_tab_changed(self, index):
        """Handle tab changes - update tabs that need refreshing"""
        if index == 1:  # Report tab
            self.birthday_tab.refresh_data()
        elif index == 2:  # Birthday tab
            self.scrape_tab.refresh_data()
        elif index == 6:  # Get results - for other clubs
            self.scrape_other_members_tab.refresh_data()
        elif index == 7:  # Get results - for other clubs
            self.scrape_other_members_tab.refresh_data()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = E1000App()
    window.show()
    sys.exit(app.exec())