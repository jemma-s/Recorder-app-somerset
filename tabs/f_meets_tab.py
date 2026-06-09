"""
TAB 6
Tab for downloading swim meet results
"""
import pandas as pd
import calendar
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from datetime import date, datetime
from Pool_meets_functions import *

class ResultsWorker(QThread):
    """A helper class so that the window won't freeze"""
    finished = pyqtSignal(object)   # emits the resulting dataframe
    error = pyqtSignal(str)         # emits an error message if something goes wrong

    def __init__(self, search_fn, *args, **kwargs):
        super().__init__()
        self.search_fn = search_fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.search_fn(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MeetsTab(QWidget):
    """Tab for downloading meet results"""
    
    def __init__(self, data_store):
        super().__init__()
        self.data_store = data_store
        self.meets_store = None
        self.results_store = None
        self._spinner_frames = ['⠋', '⠙', '⠸', '⠴', '⠦', '⠇']
        self._spinner_index = 0
        self._spinner_timer = QTimer(self)
        self._spinner_timer.timeout.connect(self._tick_spinner)
        self._spinner_msg = ""
        self.init_ui()
    
    def _start_spinner(self, message):
        """Start the loading spinner with a message"""
        self._spinner_msg = message
        self._spinner_index = 0
        self._spinner_timer.start(100)
        self._tick_spinner()

    def _stop_spinner(self):
        """Stop the loading spinner"""
        self._spinner_timer.stop()
        self.status_label.setText("")
        self.status_label.setStyleSheet("")

    def _tick_spinner(self):
        """Advance the spinner by one frame"""
        frame = self._spinner_frames[self._spinner_index % len(self._spinner_frames)]
        self.status_label.setText(f"{frame}  {self._spinner_msg}")
        self.status_label.setStyleSheet("color: var(--color-text-secondary); font-size: 14px;")
        self._spinner_index += 1
    
    def refresh_data(self):
        if not self.data_store.has_members_data():
            self.show_no_data_message()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Downloading pool meets data")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Instructions
        info = QLabel('This gets meet data directly from the <a href="https://portal.msarc.org.au/results/results.php?js=on">MSA website.</a>')
        info.setOpenExternalLinks(True)
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
        
        # Load meets button
        self.load_meets_btn = QPushButton("🏊‍♀️ Load the swim meets for the year selected")
        self.load_meets_btn.clicked.connect(self.load_meets)
        layout.addWidget(self.load_meets_btn)
        #layout.addStretch()
        
        # Status label (used for spinner + warnings)
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Meets table
        self.meets_table = QTableWidget()
        self.meets_table.setVisible(False)
        layout.addWidget(self.meets_table)

        self.meets_swimmer_combobox_helper = QLabel("Choose what results you want to find:")
        self.meets_swimmer_combobox_helper.setVisible(False)
        layout.addWidget(self.meets_swimmer_combobox_helper)
        self.combobox_helper_1 = QLabel("<b>Results of a certain meet</b><br>Creates a list of all Somerset results obtained at the swim meet selected.")
        self.combobox_helper_1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.combobox_helper_1.setVisible(False)
        layout.addWidget(self.combobox_helper_1)
        self.combobox_helper_2 = QLabel("<b>Results of a certain swimmer for the year</b><br>Creates a list of all results obtained by the selected Somerset swimmer.")
        self.combobox_helper_2.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.combobox_helper_2.setVisible(False)
        layout.addWidget(self.combobox_helper_2)
        self.combobox_helper_3 = QLabel("<b>All results in the year</b><br>Creates a list of all Somerset results at every swim meet in the year. ")
        self.combobox_helper_3.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.combobox_helper_3.setVisible(False)
        layout.addWidget(self.combobox_helper_3)
        self.combobox_helper_4 = QLabel("<b>Combined year results - For awards</b><br>Finds the total amount of world athletic points obtained by each Somerset swimmer. Points are not awarded for 25m or endurance events. ")
        self.combobox_helper_4.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.combobox_helper_4.setVisible(False)
        layout.addWidget(self.combobox_helper_4)

        self.results_combobox = QComboBox()
        self.results_combobox.addItems([
            "Results of a certain meet",
            "Results of a certain swimmer for the year",
            "All results in the year",
            "Combined year results - For awards"
        ])
        self.results_combobox.currentTextChanged.connect(self.meets_swimmer_selector)
        self.results_combobox.setVisible(False)
        layout.addWidget(self.results_combobox)

        self.status_label2 = QLabel("")
        self.status_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label2)

        self.meets_swimmer_combobox = QComboBox()
        self.meets_swimmer_combobox.setVisible(False)
        layout.addWidget(self.meets_swimmer_combobox)
        #layout.addStretch()

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
        layout.addWidget(self.download_btn)

    def load_meets(self):
        self.load_meets_btn.setEnabled(False)
        self._start_spinner("Loading swim meets, please wait...")

        self._worker = ResultsWorker(meets_list_from_url, self.year_combo.currentText())
        self._worker.finished.connect(self._on_meets_loaded)
        self._worker.error.connect(self._on_load_error)
        self._worker.start()

    def _on_meets_loaded(self, df):
        del df['URL']
        self.meets_store = df
        self.results_combobox.setVisible(True)
        self.meets_swimmer_combobox_helper.setVisible(True)
        self.combobox_helper_1.setVisible(True)
        self.combobox_helper_2.setVisible(True)
        self.combobox_helper_3.setVisible(True)
        self.combobox_helper_4.setVisible(True)
        self._stop_spinner()
        self.load_meets_btn.setEnabled(True)

    def load_results(self):
        self.load_results_btn.setEnabled(False)
        self._start_spinner("Loading results…")

        selected = self.results_combobox.currentText()
        year = self.year_combo.currentText()
        selected_swimmer = self.meets_swimmer_combobox.currentText()
        memberslist = self.data_store.members_df.copy()

        if selected == "Results of a certain swimmer for the year":
            MSWA_number = memberslist.loc[memberslist["Full name"] == selected_swimmer, "MSWA number"].item()
            firstname = memberslist.loc[memberslist["Full name"] == selected_swimmer, "First name"].item()
            surname = memberslist.loc[memberslist["Full name"] == selected_swimmer, "Surname"].item()
            self._worker = ResultsWorker(individual_swimmers_results, MSWA_number, year, firstname, surname)

        elif selected == "All results in the year":
            self._worker = ResultsWorker(all_swimmers_results, memberslist, year)

        elif selected == "Combined year results - For awards":
            self._worker = ResultsWorker(all_swimmers_results_grouped_points, memberslist, year)

        self._worker.finished.connect(self._on_results_loaded)
        self._worker.error.connect(self._on_load_error)
        self._worker.start()

    def _on_results_loaded(self, df):
        self.results_store = df
        self.display_results_table(df)
        self.download_btn.setVisible(True)
        self._stop_spinner()
        self.load_results_btn.setEnabled(True)

    def _on_load_error(self, message):
        QMessageBox.critical(self, "Error", f"Failed to load: {message}")
        self._stop_spinner()
        self.load_meets_btn.setEnabled(True)
        self.load_results_btn.setEnabled(True)

    def display_meets_table(self, df):
        """Display members data in table"""
        self.meets_table.setVisible(True)
        self.meets_table.setRowCount(len(df))
        self.meets_table.setColumnCount(len(df.columns))
        self.meets_table.setHorizontalHeaderLabels(df.columns)
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                self.meets_table.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))
        self.meets_table.resizeColumnsToContents()
        self.meets_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def display_results_table(self, df):
        """Display results data in table"""
        self.results_table.setVisible(True)
        self.results_table.setRowCount(len(df))
        self.results_table.setColumnCount(len(df.columns))
        self.results_table.setHorizontalHeaderLabels(df.columns)
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                self.results_table.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))
        self.results_table.resizeColumnsToContents()
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def meets_swimmer_selector(self):
        """Output either a list of swimmers or a list of meets to choose"""
        selected_result_combobox = self.results_combobox.currentText()
        self.meets_swimmer_combobox.clear()
        self.load_results_btn.setVisible(True)
        if not self.data_store.has_members_data():
            self.show_no_data_message()
            self.meets_swimmer_combobox.setVisible(False)
            return
        if selected_result_combobox == "Results of a certain swimmer for the year":
            memberslist = self.data_store.members_df["Full name"]
            self.meets_swimmer_combobox.addItems(memberslist.tolist())
            self.meets_swimmer_combobox.setVisible(True)
            self.status_label2.setText("Select a swimmer")
        elif selected_result_combobox == "Results of a certain meet":
            meetslist = self.meets_store['Meet']
            self.meets_swimmer_combobox.addItems(meetslist.tolist())
            self.meets_swimmer_combobox.setVisible(True)
            self.status_label2.setText("Select a swim meet")
        else:
            self.meets_swimmer_combobox.setVisible(False)
            self.status_label2.setText("")

    def show_no_data_message(self):
        """Show message when no data is available"""
        self.load_results_btn.setVisible(False)
        self.status_label.setText("⚠️ No member data loaded. Please upload members file in the '🦭 Upload Members' tab first.")
        self.status_label.setStyleSheet("color: orange; font-weight: bold; font-size: 14px;")

    def download_results(self):
        """Download results to Excel"""
        if self.results_store is None:
            return
        
        today = datetime.now().strftime("%d-%m-%Y")
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", f"Swim-meet-results-{today}.xlsx", "Excel Files (*.xlsx)")
        
        if file_path:
            try:
                self.results_store.to_excel(file_path, index=False)
                QMessageBox.information(self, "Success", "Results saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")