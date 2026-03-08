"""
TAB 3
Tab for scraping E1000 results from MSA website
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


class ScraperThreadOtherClubSelected(QThread):
    """Background thread for web scraping with progress updates"""
    progress_update = pyqtSignal(int, int, str)  # current, total, message
    scraping_complete = pyqtSignal(object)  # DataFrame
    scraping_error = pyqtSignal(str)  # error message
    
    def __init__(self, data_store, year):
        super().__init__()
        self.data_store = data_store
        self.year = year
        self.is_running = True
    
    def run(self):
        """Run the scraping in background thread"""
        try:
            print("DEBUG: Setting up driver...")
            wd = setup_driver()
            print("DEBUG: Driver setup complete")
            
            all_results = []
            df = self.data_store.get_results_selected_members_other_club_df()
            if df is None or len(df) == 0:
                self.scraping_error.emit("No member data available")
                return
            # Filtering for the selected club
            df = df[df['Club'] == self.data_store.get_selected_club()]
            
            mswa_ids = df["ID"].tolist()  # Convert to list
            total = len(mswa_ids)
            
            for idx, mswa_id in enumerate(mswa_ids):
                if not self.is_running:
                    break
                
                # Get swimmer name
                swimmer_name = self.data_store.get_selected_club_member_name(mswa_id)
                
                print(f"\nDEBUG: Processing swimmer {idx+1}/{total}, ID: {mswa_id}, Name: {swimmer_name}")
                self.progress_update.emit(idx + 1, total, f"Searching for {swimmer_name} (ID: {mswa_id})...")
                
                # Convert ID to string
                mswa_id_str = str(int(mswa_id)) if isinstance(mswa_id, float) else str(mswa_id)
                
                # Search for swimmer
                search_result = input_swimmer_search(wd, self.year, mswa_id_str)
                
                if search_result:
                    time.sleep(0.3)  # Wait for page to load
                    
                    # Extract data
                    swimmer_df = extract_swimmer_data(wd)
                    
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
        """Stop the scraping thread"""
        self.is_running = False


class ScrapeTabOtherClubSelected(QWidget):
    """Tab for scraping E1000 data from MSA website"""
    
    def __init__(self, data_store):
        super().__init__()
        self.data_store = data_store
        self.scraper_thread = None
        self.scraped_results = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Get current E1000 results - Other clubs")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Instructions
        info = QLabel("This gets endurance results directly from the MSA website (https://e1000.msarc.org.au/results/results.php)")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        # Year selection
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Select a year:"))
        self.year_combo = QComboBox()
        self.year_combo.addItems(['2022', '2023', '2024', '2025', '2026', '2027', '2028'])
        self.year_combo.setCurrentText('2026')
        year_layout.addWidget(self.year_combo)
        year_layout.addStretch()
        layout.addLayout(year_layout)

        # Info on current club selected
        self.info2 = QLabel("Current club selected: NONE")
        self.info2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info2)
        
        
        # Scrape button
        self.scrape_btn = QPushButton("🔍 Get E1000 results")
        self.scrape_btn.clicked.connect(self.start_scraping)
        self.scrape_btn.setEnabled(False)
        self.scrape_btn.setStyleSheet(self._get_scrape_button_style())
        self.scrape_btn.setMinimumHeight(50)
        layout.addWidget(self.scrape_btn)
        
        layout.addWidget(QLabel("Note: This may take multiple minutes"))
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label)
        
        # Success log
        self.success_log_label = QLabel("Successfully downloaded swimmers:")
        self.success_log_label.setVisible(False)
        layout.addWidget(self.success_log_label)
        
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
        self.download_btn.setStyleSheet(self._get_download_button_style())
        layout.addWidget(self.download_btn)
        
        layout.addStretch()
        #self.enable_start_scraping()

    def refresh_data(self):
        if self.data_store.has_selected_club() is not None:
            self.info2.setText(f"Current club selected: {self.data_store.get_selected_club()}")
            self.enable_start_scraping()
    
    def enable_start_scraping(self):
        if not self.data_store.has_results_selected_members_other_club_df():
            self.scrape_btn.setEnabled(False)
        else:
            self.scrape_btn.setEnabled(True)
    
    def start_scraping(self):
        """Start the scraping process"""
        if not self.data_store.has_results_selected_members_other_club_df():
            QMessageBox.warning(self, "Warning", "Please select a club first!")
            return
        
        self.scrape_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting download...")
        
        self.success_log.clear()
        self.success_log.setVisible(True)
        self.success_log_label.setVisible(True)
        
        year = self.year_combo.currentText()
        
        self.scraper_thread = ScraperThreadOtherClubSelected(self.data_store, year)
        self.scraper_thread.progress_update.connect(self.update_progress)
        self.scraper_thread.scraping_complete.connect(self.scraping_finished)
        self.scraper_thread.scraping_error.connect(self.scraping_failed)
        self.scraper_thread.start()
    
    def update_progress(self, current, total, message):
        """Update progress bar and label"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"Swimmer {current}/{total}: {message}")
        
        if "Found" in message and "✓" in message:
            self.success_log.append(f"✓ {message}")
            self.success_log.verticalScrollBar().setValue(
                self.success_log.verticalScrollBar().maximum())
    
    def scraping_finished(self, df):
        """Handle scraping completion"""
        self.data_store.set_results_other_club_data(df)
        self.progress_label.setText(f"✓ Download complete! Found {len(df)} total swims")
        self.progress_label.setStyleSheet("color: green; font-weight: bold;")
        self.scrape_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        
        self.display_results_table(df)
        QMessageBox.information(self, "Success", f"Successfully downloaded {len(df)} swims!")
    
    def scraping_failed(self, error_msg):
        """Handle scraping error"""
        self.progress_label.setText(f"✗ Error: {error_msg}")
        self.progress_label.setStyleSheet("color: red; font-weight: bold;")
        self.scrape_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Download failed: {error_msg}")
    
    def display_members_table(self, df):
        """Display members data in table"""
        self.members_table.setVisible(True)
        self.members_table.setRowCount(len(df))
        self.members_table.setColumnCount(len(df.columns))
        self.members_table.setHorizontalHeaderLabels(df.columns)
        
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                item = QTableWidgetItem(str(df.iloc[i, j]))
                self.members_table.setItem(i, j, item)
        
        self.members_table.resizeColumnsToContents()
        header = self.members_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
    def display_results_table(self, df):
        """Display results in table"""
        if df is None or len(df) == 0:
            return
        
        self.results_table.setVisible(True)
        self.results_table.setRowCount(min(len(df), 100))
        self.results_table.setColumnCount(len(df.columns))
        self.results_table.setHorizontalHeaderLabels(df.columns)
        
        for i in range(min(len(df), 100)):
            for j, col in enumerate(df.columns):
                self.results_table.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))
        
        self.results_table.resizeColumnsToContents()
    
    def download_results(self):
        """Download results to Excel"""
        if not self.data_store.has_results_other_club_data():
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "E1000-results.xlsx", "Excel Files (*.xlsx)")
        
        if file_path:
            try:
                self.data_store.results_other_club_df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Success", "Results saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
    
    
    def _get_scrape_button_style(self):
        return """
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
            QPushButton:disabled {
                background-color: #94a3b8;
                color: #e2e8f0;
            }
        """
    
    def _get_download_button_style(self):
        return """
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
            QPushButton:disabled {
                background-color: #94a3b8;
                color: #e2e8f0;
            }
        """