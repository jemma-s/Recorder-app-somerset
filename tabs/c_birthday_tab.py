"""
TAB 3
Tab for viewing swimmer birthdays by month
"""
import pandas as pd
import calendar
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView)
from PyQt6.QtCore import Qt
from datetime import date
from datetime import datetime


class BirthdayTab(QWidget):
    """Tab for viewing swimmer birthdays by month"""
    
    def __init__(self, data_store):
        super().__init__()
        self.data_store = data_store
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Birthday Calendar")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Instructions
        info = QLabel("The birthdays of the current Somerset Masters members")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        info2 = QLabel("Note: This only includes members who are signed up through SwimCentral. It does not include the birthdays of social or life members.")
        info2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info2)
        
        # Month selector
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Select Month:"))
        self.month_combo = QComboBox()
        # Setting the default option to 'All months'
        self.month_combo.addItem("All months", None)
        for i in range(1, 13):
            self.month_combo.addItem(calendar.month_name[i], i)
        self.month_combo.currentIndexChanged.connect(self.update_birthdays)
        self.month_combo.setCurrentIndex(0)
        filter_layout.addWidget(self.month_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Summary statistics - returns the number of birthdays in each month
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("font-size: 12px; color: #666; margin: 10px;")
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.summary_label)
        
        # Birthday table
        self.birthday_table = QTableWidget()
        layout.addWidget(self.birthday_table)
        
        layout.addStretch()
        
        # Initial message
        self.update_birthdays()

    def refresh_data(self):
        self.update_birthdays()
    
    def update_birthdays(self):
        """Update the birthday table based on selected month"""
        if not self.data_store.has_members_data():
            self.show_no_data_message()
            return
        
        try:
            df = self.data_store.members_df.copy()
            
            # Check for DOB column
            dob_col = None
            for col in ['DOB', 'Date of Birth', 'dob']:
                if col in df.columns:
                    dob_col = col
                    break
            
            if dob_col is None:
                self.status_label.setText("❌ No date of birth column found in member data")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
                self.birthday_table.setRowCount(0)
                return
            
            # Parse dates
            df['DOB_parsed'] = pd.to_datetime(df[dob_col], errors='coerce')
            df = df.dropna(subset=['DOB_parsed'])
            
            if df.empty:
                self.status_label.setText("❌ No valid dates found in DOB column")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
                self.birthday_table.setRowCount(0)
                return
            
            df['Birth_Month'] = df['DOB_parsed'].dt.month
            df['Birth_Day'] = df['DOB_parsed'].dt.day
            df['Birth_Date'] = df['DOB_parsed'].dt.strftime('%d/%m/%Y')
            df['Birth_Year'] = df['DOB_parsed'].dt.year
            df['Age'] = df['DOB_parsed'].apply(calculate_age)

            # Get selected month
            selected_month = self.month_combo.currentData()
            
            # Filter by month if selected
            if selected_month:
                df_filtered = df[df['Birth_Month'] == selected_month]
                df_filtered = df_filtered.sort_values('Birth_Day')
                month_name = calendar.month_name[selected_month]
            else:
                df_filtered = df.sort_values(['Birth_Month', 'Birth_Day'])
                month_name = "All months"
            
            # Prepare table data
            display_cols = ['Full name', 'Birth_Day', 'Birth_Date', 'Age']

            
            if 'MSWA number' in df_filtered.columns:
                display_cols.insert(0, 'MSWA number')
            
            display_df = df_filtered[display_cols].copy()
            
            # Rename columns for display
            column_names = ["MSWA number", "Name", "Day", "Birthday", "Current age"]
            
            display_df.columns = column_names
            
            # Display in table
            self.display_birthday_table(display_df)
            
            # Update status and summary
            self.status_label.setText(f"Showing birthdays for {month_name}")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            
            # Generate summary statistics
            if selected_month is None:
                month_counts = df.groupby('Birth_Month').size()
                summary_text = "Birthdays per month: " + ", ".join(
                    [f"{month}: {count}" for month, count in month_counts.items()])
                self.summary_label.setText(summary_text)
            else:
                self.summary_label.setText(f"Total birthdays in {month_name}: {len(df_filtered)}")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error processing birthdays: {str(e)}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.birthday_table.setRowCount(0)
    
    def display_birthday_table(self, df):
        """Display birthday data in table widget"""
        self.birthday_table.setRowCount(len(df))
        self.birthday_table.setColumnCount(len(df.columns))
        self.birthday_table.setHorizontalHeaderLabels(df.columns)
        
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                item = QTableWidgetItem(str(df.iloc[i, j]))
                
                # Center align MSWA number, Day and Current age
                if col in ['MSWA number', 'Day', 'Current age']:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                self.birthday_table.setItem(i, j, item)
        
        self.birthday_table.resizeColumnsToContents()
        
        # Stretch the name column
        header = self.birthday_table.horizontalHeader()
        name_col_idx = list(df.columns).index('Name') if 'Name' in df.columns else 1
        header.setSectionResizeMode(name_col_idx, QHeaderView.ResizeMode.Stretch)
    
    def show_no_data_message(self):
        """Show message when no data is available"""
        self.status_label.setText("⚠️ No member data loaded. Please upload members file in the '🦭 Upload Members Data' tab first. \nAlready loaded in member data❓ Try selecting a month")
        #self.status_label.setText(" /n")
        self.status_label.setStyleSheet("color: orange; font-weight: bold; font-size: 14px;")
        self.summary_label.setText("")
        self.birthday_table.setRowCount(0)
        self.birthday_table.setColumnCount(0)


def calculate_age(born):
    born = born.date()  
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))