# Somerset Masters Swimming - E1000 PyQt6 Application

A desktop GUI application built with PyQt6 for managing Somerset Masters Swimming E1000 endurance program data.

## 📁 Project Structure

```
project/
│
├── main.py                    # Main application entry point
├── shared_data.py             # Shared data storage class
├── EM1000_functions.py        # Your existing web scraping functions
│
├── tabs/
│   ├── __init__.py           # Package initializer
│   ├── scrape_tab.py         # Tab for scraping E1000 data
│   ├── visualize_tab.py      # Tab for uploading results
│   ├── report_tab.py         # Tab for leaderboard/reports
│   └── birthday_tab.py       # Tab for birthday calendar
│
├── assets/
│   └── somerset_logo.jpg     # Club logo (optional)
│
└── requirements.txt           # Python dependencies
```

## 🚀 Installation

### 1. Create the folder structure:
```bash
mkdir -p tabs assets
```

### 2. Install dependencies:
```bash
pip install PyQt6 pandas openpyxl selenium webdriver-manager
```

### 3. Create `requirements.txt`:
```
PyQt6>=6.6.0
pandas>=2.0.0
openpyxl>=3.1.0
selenium>=4.15.0
webdriver-manager>=4.0.0
```

## 📂 File Placement

1. **Main files** (in root directory):
   - `main.py` - Main application
   - `shared_data.py` - Data storage
   - `EM1000_functions.py` - Your existing scraper code

2. **Tab files** (in `tabs/` directory):
   - `__init__.py`
   - `scrape_tab.py`
   - `visualize_tab.py`
   - `report_tab.py`
   - `birthday_tab.py`

3. **Assets** (optional):
   - Place club logo in `assets/somerset_logo.jpg`

## 🏃 Running the Application

```bash
python main.py
```

## 📱 Using the Application

### Tab 1: 📥 Get E1000 Data
1. Select the year (default: 2025)
2. Upload members file from Swim Central (Excel or CSV)
3. Click "Get E1000 results" to scrape data from MSA website
4. Wait for scraping to complete (may take several minutes)
5. Download results as Excel file

**Members file format:**
- Must contain `MSWA number` column
- Optional: `First name`, `Surname`, `DOB`, `Gender`, `Status`

### Tab 2: 📊 Visualize Data
1. Upload previously downloaded E1000 results Excel file
2. Data will be loaded for viewing in other tabs

### Tab 3: 📋 E1000 Report
1. View leaderboard of swimmers by total points
2. Filter by gender (Both/Male/Female)
3. See placing with medals (🏆🥈🥉) and perfection scores

### Tab 4: 🎂 Birthday Calendar
1. View swimmer birthdays organized by month
2. Filter by specific month or view all
3. See birthday distribution statistics

## 🔧 Best Practices Applied

✅ **Modular architecture**: Each tab is a separate class in its own file
✅ **Shared data store**: Centralized DataStore class for cross-tab data access
✅ **Separation of concerns**: UI logic separate from business logic
✅ **Reusable components**: Each tab can be developed/tested independently
✅ **Type hints and docstrings**: Well-documented code
✅ **Error handling**: User-friendly error messages and validation

## 🎨 Features

- **Modern UI**: Clean, professional interface with custom styling
- **Background processing**: Web scraping runs in separate thread (no UI freezing)
- **Progress tracking**: Real-time progress bar and success log
- **Data persistence**: Save and reload results between sessions
- **Multiple filters**: Gender and month filtering for reports
- **Table views**: Sortable, scrollable data tables

## 🐛 Troubleshooting

**Import errors**: Make sure all files are in the correct directories and `tabs/__init__.py` exists

**Chrome driver issues**: The app uses `webdriver-manager` to automatically download ChromeDriver

**Data not showing**: Ensure you've uploaded/scraped data before viewing reports

**Somerset_points.xlsx not found**: Update the path in `main.py` or comment out if not needed

## 📝 Customization

### Changing the Somerset points file path:
Edit `main.py`, line ~24:
```python
self.data_store.e1000_sheet = pd.read_excel("YOUR_PATH_HERE/Somerset_points.xlsx")
```

### Adding a logo:
Place your club logo at `assets/somerset_logo.jpg` (or update path in `main.py`)

### Modifying styles:
Each tab has its own styling in button style methods (search for `setStyleSheet`)

## 🔄 Differences from Original Code

- **Modular structure**: Split into multiple files instead of one large file
- **Shared data**: DataStore class replaces instance variables
- **Tab classes**: Each tab is now a separate QWidget class
- **Birthday tab**: New feature for viewing member birthdays
- **Better organization**: Clear separation between UI and logic

## 💡 Future Enhancements

- Add matplotlib/plotly charts to visualization tab
- Export reports to PDF
- Email birthday reminders
- Import/export settings
- Database storage instead of in-memory

## 📞 Support

For issues or questions, contact your Somerset Masters Swimming administrator.