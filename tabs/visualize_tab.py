"""
Tab for uploading and visualizing E1000 data
Save as: tabs/visualize_tab.py
"""
import pandas as pd
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt


class VisualizeTab(QWidget):
    """Tab for uploading existing E1000 results and viewing visualizations"""
    
    def __init__(self, data_store):
        super().__init__()
        self.data_store = data_store
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Visualise current E1000 data")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

        # Instructions
        info1 = QLabel("If you have already downloaded the current E1000 results, you can look at the results here")
        info1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info1)
        
        info2 = QLabel("Upload the results excel file from 'Get current E1000 data'")
        info2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info2)
        
        # Upload button
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

        # Upload status
        self.upload_status = QLabel("")
        self.upload_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.upload_status)
        
        # Placeholder for future visualizations
        viz_note = QLabel("\n\n📊 Interactive visualizations coming soon!\n\n"
                         "For now, after uploading results, switch to the 'E1000 Report' tab\n"
                         "to view leaderboard and statistics.")
        viz_note.setStyleSheet("color: #666; font-style: italic; font-size: 14px;")
        viz_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(viz_note)
        
        layout.addStretch()
    
    def upload_results_file(self):
        """Upload existing results file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Results File", "", 
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)")
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                # Validate required columns
                required_cols = ['Name', 'Point']
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    QMessageBox.warning(self, "Warning", 
                        f"Missing expected columns: {', '.join(missing_cols)}\n\n"
                        "This might not be an E1000 results file.")
                
                self.data_store.set_results_data(df)
                self.upload_status.setText(f"✓ Loaded {len(df)} results from {file_path.split('/')[-1]}")
                self.upload_status.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
                
                # Show success message
                QMessageBox.information(self, "Success", 
                    f"Successfully loaded {len(df)} swim results!\n\n"
                    "Switch to the 'E1000 Report' tab to view the leaderboard.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
                self.upload_status.setText("❌ Failed to load file")
                self.upload_status.setStyleSheet("color: red; font-weight: bold;")