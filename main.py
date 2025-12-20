import sys
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                             QComboBox, QProgressBar, QTableWidget, QTableWidgetItem,
                             QTabWidget, QMessageBox, QHeaderView)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# Import your scraping functions
from EM1000_functions import scrape_all_swimmers, setup_driver, input_swimmer_search, extract_swimmer_data
import time

class ScraperThread(QThread):
    """Background thread for web scraping with progress updates."""
    progress_update = pyqtSignal(int, int, str)  # current, total, swimmer_name
    scraping_complete = pyqtSignal(object)  # DataFrame
    scraping_error = pyqtSignal(str)  # error message
    
    def __init__(self, mswa_ids, year, members_df):
        super().__init__()
        self.mswa_ids = mswa_ids
        self.year = year
        self.members_df = members_df
        self.is_running = True
    
    def run(self):
        """Run the scraping in background thread."""
        try:
            # Import the functions from your module
            from EM1000_functions import setup_driver, input_swimmer_search, extract_swimmer_data
            
            print("DEBUG: Setting up driver...")
            wd = setup_driver()
            print("DEBUG: Driver setup complete")
            
            all_results = []
            total = len(self.mswa_ids)
            
            for idx, mswa_id in enumerate(self.mswa_ids):
                if not self.is_running:
                    break
                
                # Get swimmer name from members_df
                swimmer_name = "Unknown"
                try:
                    member_row = self.members_df[self.members_df["MSWA number"] == mswa_id]
                    if len(member_row) > 0:
                        if "First name" in self.members_df.columns and "Surname" in self.members_df.columns:
                            first = member_row["First name"].iloc[0]
                            last = member_row["Surname"].iloc[0]
                            swimmer_name = f"{first} {last}"
                except:
                    pass
                
                print(f"\nDEBUG: Processing swimmer {idx+1}/{total}, ID: {mswa_id}, Name: {swimmer_name}")
                self.progress_update.emit(idx + 1, total, f"Searching for {swimmer_name} (ID: {mswa_id})...")
                
                # Convert ID to string without decimal
                mswa_id_str = str(int(mswa_id)) if isinstance(mswa_id, float) else str(mswa_id)
                print(f"DEBUG: Using ID string: {mswa_id_str}")
                
                # Use your function to search
                search_result = input_swimmer_search(wd, self.year, mswa_id_str)
                print(f"DEBUG: Search result for {mswa_id}: {search_result}")
                
                if search_result:
                    time.sleep(0.3)  # Wait for page to load
                    
                    # Use your function to extract data
                    print(f"DEBUG: Extracting data for {mswa_id}...")
                    swimmer_df = extract_swimmer_data(wd)
                    print(f"DEBUG: Extraction result: {swimmer_df is not None}, rows: {len(swimmer_df) if swimmer_df is not None else 0}")
                    
                    if swimmer_df is not None and len(swimmer_df) > 0:
                        all_results.append(swimmer_df)
                        swimmer_name = swimmer_df['Name'].iloc[0]
                        result_count = len(swimmer_df)
                        print(f"DEBUG: SUCCESS - {swimmer_name} has {result_count} results")
                        self.progress_update.emit(idx + 1, total, 
                                                f"{swimmer_name} - Found {result_count} results ✓")
                    else:
                        print(f"DEBUG: No data extracted for {mswa_id}")
                        self.progress_update.emit(idx + 1, total, f"ID {mswa_id} - No results found")
                else:
                    print(f"DEBUG: Search failed for {mswa_id}")
                    self.progress_update.emit(idx + 1, total, f"ID {mswa_id} - Search failed")
                
                time.sleep(0.1)
            
            print("DEBUG: Closing driver...")
            wd.quit()
            print("DEBUG: Driver closed")
            
            # Combine results
            if all_results:
                combined_df = pd.concat(all_results, ignore_index=True)
                print(f"DEBUG: Combined {len(combined_df)} total results")
                self.scraping_complete.emit(combined_df)
            else:
                print("DEBUG: No results found for any swimmers")
                self.scraping_complete.emit(pd.DataFrame())
                
        except Exception as e:
            print(f"DEBUG ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            self.scraping_error.emit(str(e))
    
    def stop(self):
        """Stop the scraping thread."""
        self.is_running = False


class E1000App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Somerset Masters Swimming - E1000")
        self.setGeometry(100, 100, 1600, 900)
        
        # Data storage
        self.members_df = None
        self.results_df = None
        self.e1000_sheet = pd.read_excel("C:/Users/Arinda/Documents/Somerset/Downloading MSA Results/Data Files/Somerset_points.xlsx")
        
        # Setup UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_scrape_tab(), "Get current E1000 data")
        self.tabs.addTab(self.create_upload_tab(), "Visualise current E1000 data")
        self.tabs.addTab(self.create_report_tab(), "E1000 Report")
        
        main_layout.addWidget(self.tabs)
    
    def create_header(self):
        """Create header with logo and title."""
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
    
    def create_scrape_tab(self):
        """Create the scraping tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Instructions
        title = QLabel("Get current E1000 results")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        info = QLabel("This gets endurance results directly from the MSA website (https://e1000.msarc.org.au/results/results.php)")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        info2 = QLabel("Before proceeding, download the members report from Swim Central - or ask someone with access to send it to you")
        info2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info2)
        
        # Year selection
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Select a year:"))
        self.year_combo = QComboBox()
        self.year_combo.addItems(['2022', '2023', '2024', '2025', '2026', '2027', '2028'])
        self.year_combo.setCurrentText('2025')
        year_layout.addWidget(self.year_combo)
        year_layout.addStretch()
        layout.addLayout(year_layout)
        
        # Upload button
        self.upload_btn = QPushButton("📁 Upload members file (excel or csv)")
        self.upload_btn.clicked.connect(self.upload_members_file)
        self.upload_btn.setStyleSheet("""
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
        """)
        self.upload_btn.setMinimumHeight(60)
        layout.addWidget(self.upload_btn)
        infoupload = QLabel("Note: Make sure the file is in the following format")
        infoupload2 = QLabel("First name | Surname | DOB | Gender | Account status | Add date | Membership type | MSWA Number | Club")
        layout.addWidget(infoupload)
        layout.addWidget(infoupload2)
        layout.addSpacing(10)


        
        # File status
        self.file_status = QLabel("")
        layout.addWidget(self.file_status)
        
        # Members table
        self.members_table = QTableWidget()
        self.members_table.setVisible(False)
        self.members_table.setMaximumHeight(300)
        layout.addWidget(self.members_table)
        layout.addSpacing(50)
        
        # Scrape button
        self.scrape_btn = QPushButton("🔍 Get E1000 results")
        self.scrape_btn.clicked.connect(self.start_scraping)
        self.scrape_btn.setEnabled(False)
        self.scrape_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E40AF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e3a8a;
            }
            QPushButton:pressed {
                background-color: #1e3a8a;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
                color: #e2e8f0;
            }
        """)
        self.scrape_btn.setMinimumHeight(50)
        layout.addWidget(self.scrape_btn)
        inforesults= QLabel("Note: This may take multiple minutes")
        layout.addWidget(inforesults)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label)
        
        # Success log (scrollable list)
        self.success_log_label = QLabel("Successfully downloaded swimmers:")
        self.success_log_label.setVisible(False)
        layout.addWidget(self.success_log_label)
        
        from PyQt6.QtWidgets import QTextEdit
        self.success_log = QTextEdit()
        self.success_log.setReadOnly(True)
        self.success_log.setMaximumHeight(150)
        self.success_log.setVisible(False)
        layout.addWidget(self.success_log)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setVisible(False)
        layout.addWidget(self.results_table)
        
        # Download button
        layout.addSpacing(50)
        self.download_btn = QPushButton("📥 Download results excel")
        self.download_btn.clicked.connect(self.download_results)
        self.download_btn.setEnabled(False)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
                color: #e2e8f0;
            }
        """)
        layout.addWidget(self.download_btn)
        
        layout.addStretch()
        return tab
    
    def create_upload_tab(self):
        """Create the upload tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title = QLabel("Visualise current E1000 data")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

        infoupload = QLabel("If you have already downloaded the current E1000 results, you can look at the results here")
        infoupload2 = QLabel("Upload the results excel file from 'Get current E1000 data'")
        layout.addWidget(infoupload)
        layout.addWidget(infoupload2)
        
        self.upload_results_btn = QPushButton("📁 Upload E1000 results (excel)")
        self.upload_results_btn.clicked.connect(self.upload_results_file)
        self.upload_results_btn.setStyleSheet("""
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
        """)
        self.upload_results_btn.setMinimumHeight(60)
        layout.addWidget(self.upload_results_btn)

        self.upload_status = QLabel("")
        layout.addWidget(self.upload_status)
        
        layout.addStretch()
        return tab
    
    def create_report_tab(self):
        """Create the report/visualization tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title = QLabel("E1000 Report")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Gender filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Select a gender:"))
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(['Both', 'Female', 'Male'])
        self.gender_combo.currentTextChanged.connect(self.update_report)
        filter_layout.addWidget(self.gender_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Leaderboard table
        self.leaderboard_table = QTableWidget()
        layout.addWidget(self.leaderboard_table)
        
        # Note about visualizations
        viz_note = QLabel("Full interactive visualizations coming soon!\nFor now, use the uploaded Excel with Plotly/Dash for detailed charts.")
        viz_note.setStyleSheet("color: #666; font-style: italic; margin: 20px;")
        layout.addWidget(viz_note)
        
        layout.addStretch()
        return tab
    
    def upload_members_file(self):
        """Upload members file (CSV or Excel)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Members File", "", "All Supported Files (*.xlsx *.xls *.csv);;Excel Files (*.xlsx *.xls);;CSV Files (*.csv)")
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    # CSV format has headers
                    if "MSWA number" not in df.columns:
                        # Try to map columns if they're in different order
                        df.columns = ["First name", "Surname", "DOB", "Gender", "Status", 
                                    "Start date", "Member type", "MSWA number", "Club"]
                else:
                    # Excel format - try with headers first
                    df_test = pd.read_excel(file_path, nrows=1)
                    if "MSWA number" in df_test.columns or "MSWA number" in str(df_test.values):
                        # Has headers
                        df = pd.read_excel(file_path)
                    else:
                        # No headers - old format
                        df = pd.read_excel(file_path, header=None)
                        df.columns = ["First name", "Surname", "Age", "DOB", "Gender", "x", 
                                    "Membership type", "Start date", "End date", "Status", 
                                    "MSWA number", "y"]
                        df = df.drop(columns=['x', 'y'])
                
                # Ensure MSWA number column exists
                if "MSWA number" not in df.columns:
                    raise ValueError("Could not find 'MSWA number' column in file")
                
                # Filter active members only
                if "Status" in df.columns:
                    df = df[df.Status != "Terminated"]
                
                self.members_df = df
                
                # Display members in table
                self.display_members_table(df)
                
                self.file_status.setText(f"✓ Loaded {len(df)} active members from {file_path.split('/')[-1]}")
                self.file_status.setStyleSheet("color: green; font-weight: bold;")
                self.scrape_btn.setEnabled(True)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}\n\nPlease ensure the file contains a 'MSWA number' column.")
    
    def start_scraping(self):
        """Start the scraping process in background thread."""
        if self.members_df is None:
            QMessageBox.warning(self, "Warning", "Please upload members file first!")
            return
        
        # Disable button and show progress
        self.scrape_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting download...")
        
        # Clear and show success log
        self.success_log.clear()
        self.success_log.setVisible(True)
        self.success_log_label.setVisible(True)
        
        # Start scraper thread
        year = self.year_combo.currentText()
        # Convert to int to remove decimal points
        mswa_ids = [int(x) for x in self.members_df["MSWA number"].dropna().tolist()]
        
        print(f"DEBUG: Starting download for {len(mswa_ids)} swimmers, year {year}")
        print(f"DEBUG: First 3 IDs: {mswa_ids[:3]}")
        
        self.scraper_thread = ScraperThread(mswa_ids, year, self.members_df)
        self.scraper_thread.progress_update.connect(self.update_progress)
        self.scraper_thread.scraping_complete.connect(self.scraping_finished)
        self.scraper_thread.scraping_error.connect(self.scraping_failed)
        self.scraper_thread.start()
        
        print("DEBUG: Thread started")
    
    def update_progress(self, current, total, message):
        """Update progress bar and label."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"Swimmer {current}/{total}: {message}")
        
        # If it's a success message (contains "Found" and "✓"), add to log
        if "Found" in message and "✓" in message:
            self.success_log.append(f"✓ {message}")
            # Auto-scroll to bottom
            self.success_log.verticalScrollBar().setValue(
                self.success_log.verticalScrollBar().maximum()
            )
    
    def scraping_finished(self, df):
        """Handle scraping completion."""
        self.results_df = df
        self.progress_label.setText(f"✓ Download complete! Found {len(df)} total swims")
        self.progress_label.setStyleSheet("color: green; font-weight: bold;")
        self.scrape_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        
        # Display results in table
        self.display_results_table(df)
        
        # Update report tab
        self.update_report()
        
        QMessageBox.information(self, "Success", 
                              f"Successfully downloaded {len(df)} swims!")
    
    def scraping_failed(self, error_msg):
        """Handle scraping error."""
        self.progress_label.setText(f"✗ Error: {error_msg}")
        self.progress_label.setStyleSheet("color: red; font-weight: bold;")
        self.scrape_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Download failed: {error_msg}")
    
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
                item = QTableWidgetItem(str(df.iloc[i, j]))
                self.members_table.setItem(i, j, item)
        
        self.members_table.resizeColumnsToContents()
        header = self.members_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
    def display_results_table(self, df):
        """Display results in table widget."""
        if df is None or len(df) == 0:
            return
        
        self.results_table.setVisible(True)
        self.results_table.setRowCount(min(len(df), 100))  # Show first 100
        self.results_table.setColumnCount(len(df.columns))
        self.results_table.setHorizontalHeaderLabels(df.columns)
        
        for i in range(min(len(df), 100)):
            for j, col in enumerate(df.columns):
                self.results_table.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))
        
        self.results_table.resizeColumnsToContents()
    
    def download_results(self):
        """Download results to Excel."""
        if self.results_df is None:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "E1000-results.xlsx", "Excel Files (*.xlsx)")
        
        if file_path:
            try:
                self.results_df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Success", "Results saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
    
    def upload_results_file(self):
        """Upload existing results file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Results File", "", "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)")
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                self.results_df = df
                self.upload_status.setText(f"✓ Loaded {len(df)} results")
                self.upload_status.setStyleSheet("color: green; font-weight: bold;")
                
                # Update report
                self.update_report()
                self.tabs.setCurrentIndex(2)  # Switch to report tab
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
    
    def update_report(self):
        """Update the leaderboard report."""
        if self.results_df is None or len(self.results_df) == 0:
            return
        
        df = self.results_df.copy()
        
        # Apply gender filter
        gender = self.gender_combo.currentText()
        if gender == "Male":
            df = df[df["Sex"] == "M"]
        elif gender == "Female":
            df = df[df["Sex"] == "F"]
        
        # Calculate leaderboard
        df["Point"] = pd.to_numeric(df["Point"])
        leaderboard = df.groupby('Name')["Point"].sum().reset_index(name="Total points")
        leaderboard = leaderboard.sort_values(by="Total points", ascending=False)
        leaderboard['Placing'] = leaderboard['Total points'].rank(method='dense', ascending=False).astype(int)
        leaderboard = leaderboard[['Placing', 'Name', 'Total points']]
        
        # Add medals
        leaderboard['Placing'] = leaderboard['Placing'].astype(str)
        leaderboard.loc[leaderboard['Placing'] == '1', 'Placing'] += " 🏆"
        leaderboard.loc[leaderboard['Placing'] == '2', 'Placing'] += " 🥈"
        leaderboard.loc[leaderboard['Placing'] == '3', 'Placing'] += " 🥉"
        
        # Perfection score
        max_score = (self.e1000_sheet['Points_max'] * self.e1000_sheet['Count_max']).sum()
        leaderboard['Perfection score'] = leaderboard['Total points'].apply(
            lambda x: f"{(x / max_score * 100):.2f}%")
        
        # Display in table
        self.leaderboard_table.setRowCount(len(leaderboard))
        self.leaderboard_table.setColumnCount(len(leaderboard.columns))
        self.leaderboard_table.setHorizontalHeaderLabels(leaderboard.columns)
        
        for i in range(len(leaderboard)):
            for j, col in enumerate(leaderboard.columns):
                self.leaderboard_table.setItem(i, j, QTableWidgetItem(str(leaderboard.iloc[i, j])))
        
        self.leaderboard_table.resizeColumnsToContents()
        header = self.leaderboard_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = E1000App()
    window.show()
    sys.exit(app.exec())