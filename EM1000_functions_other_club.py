import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import pandas as pd
import time
from bs4 import BeautifulSoup
import plotly.express as px
import plotly.io as pio

# Setup WebDriver

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Global variable to track progress (for Dash integration)
_scraping_progress = {
    "current": 0,
    "total": 0,
    "swimmer_name": "",
    "status": "idle"  # idle, running, complete, error
}

def get_scraping_progress():
    """Get current scraping progress (for Dash callbacks)."""
    return _scraping_progress.copy()

def reset_scraping_progress():
    """Reset progress to idle state."""
    global _scraping_progress
    _scraping_progress = {
        "current": 0,
        "total": 0,
        "swimmer_name": "",
        "status": "idle"
    }

def setup_driver():
    """Initialize Chrome driver with headless options."""
    url = "https://e1000.msarc.org.au/results/results.php"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    wd = webdriver.Chrome(options=options)
    wd.get(url)
    return wd

def input_swimmer_search(wd, year, swimmer_name):
    """
    Input search criteria for a swimmer.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Select year
        year_element = wd.find_element(By.XPATH, 
            "/html/body/center/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td[1]/select")
        select = Select(year_element)
        select.select_by_visible_text(year)
        
        # Input name
        id_element = wd.find_element(By.XPATH, 
            "/html/body/center/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td[2]/div/input")
        id_element.clear()  # Clear any previous input
        id_element.send_keys(swimmer_name)
        
        # Click Show button
        show_button = wd.find_element(By.XPATH, 
            "/html/body/center/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td[4]")
        show_button.click()
        
        time.sleep(0.2)  # Wait for page to update
        return True
        
    except NoSuchElementException as e:
        print(f"Element not found for swimmer {swimmer_name}: {e}")
        return False
    except Exception as e:
        print(f"Error searching for swimmer {swimmer_name}: {e}")
        return False

def extract_swimmer_data(wd):
    """
    Extract swimmer results from the current page.
    
    Returns:
        pd.DataFrame or None: DataFrame with results, or None if no data
    """
    try:
        # Get all table rows
        all_rows = wd.find_elements(By.XPATH, 
            "/html/body/center/table/tbody/tr/td/table[4]/tbody/tr")
        
        if not all_rows:
            print("No results table found")
            return None
        
        # Extract swimmer name from first row
        name_text = all_rows[0].text
        name_only = name_text.split("[")[0].strip()
        last, first = [part.strip() for part in name_only.split(",")]
        clean_name = f"{first} {last}"
        print(f"Currently processing {clean_name}")
        
        # Extract data rows (skip headers and empty rows)
        data = []
        for i, row in enumerate(all_rows):
            row_text = row.text.strip()
            
            # Skip if: first 3 rows, header rows (contain "Point:" or "MSA ID"), or empty
            if (i < 3 or 
                "Point:" in row_text or 
                "MSA ID" in row_text or 
                not row_text):
                continue
            
            cols = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
            
            # Only add rows with the expected number of columns (12)
            if len(cols) == 12:
                data.append(cols)
        
        if not data:
            print(f"No swim data found for {clean_name}")
            return None
        
        # Create DataFrame
        colnames = ["MSA ID", "Club", "Sex", "AgeGrp", "Course", "Distance", 
                    "Stroke", "Result", "Split", "Point", "Date", "Location"]
        df = pd.DataFrame(data, columns=colnames)
        df['Name'] = clean_name
        
        # Filter out zero-point swims
        df = df[df["Point"] != '0']
        
        # Debug: print if we filtered everything out
        if len(data) > 0 and len(df) == 0:
            print(f"  ⚠ Warning: All {len(data)} swims for {clean_name} were 0 points and filtered out")
        
        return df if len(df) > 0 else None
        
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None

def scrape_all_swimmers(swimmer_names, year, progress_callback=None):
    """
    Scrape results for multiple swimmers efficiently using a single browser instance.
    
    Args:
        swimmer_names: List or Series of swimmer names in the correct format to search
        year: Year to search (e.g., "2025")
        progress_callback: Optional function to call with progress updates
        
    Returns:
        pd.DataFrame: Combined results for all swimmers
    """
    global _scraping_progress
    
    wd = setup_driver()
    all_results = []
    
    _scraping_progress["status"] = "running"
    _scraping_progress["total"] = len(swimmer_names)
    
    try:
        for idx, swimmer_name in enumerate(swimmer_names):
            _scraping_progress["current"] = idx + 1
            _scraping_progress["swimmer_name"] = f"Processing ID: {swimmer_name}"
            
            print(f"\nProcessing swimmer {idx+1}/{len(swimmer_names)}: {swimmer_name}")
            
            # Search for swimmer
            if input_swimmer_search(wd, year, swimmer_name):
                # Extract data
                swimmer_df = extract_swimmer_data(wd)
                
                if swimmer_df is not None:
                    all_results.append(swimmer_df)
                    print(f"  ✓ Found {len(swimmer_df)} results")
                    _scraping_progress["swimmer_name"] = f"{swimmer_df['Name'].iloc[0]} - {len(swimmer_df)} results"
                else:
                    print(f"  ✗ No results for {swimmer_name}")
            else:
                print(f"  ✗ Search failed for {swimmer_name}")
            
            # Progress callback
            if progress_callback:
                progress_callback(idx + 1, len(swimmer_name))
            
            time.sleep(0.1)  # Brief delay between swimmers
        
        _scraping_progress["status"] = "complete"
            
    except Exception as e:
        _scraping_progress["status"] = "error"
        _scraping_progress["swimmer_name"] = f"Error: {str(e)}"
        raise
    finally:
        wd.quit()
    
    # Combine all results
    if all_results:
        combined_df = pd.concat(all_results, ignore_index=True)
        print(f"\n✓ Successfully scraped {len(combined_df)} total results from {len(all_results)} swimmers")
        return combined_df
    else:
        print("\n✗ No results found for any swimmers")
        return pd.DataFrame()



'''
def setup_driver():
    """Initialize Chrome driver with headless options."""
    url = "https://e1000.msarc.org.au/results/results.php"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    wd = webdriver.Chrome(options=options)
    wd.get(url)
    return wd

def input_swimmer_search(wd, year, mswa_id):
    """
    Input search criteria for a swimmer.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Select year
        year_element = wd.find_element(By.XPATH, 
            "/html/body/center/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td[1]/select")
        select = Select(year_element)
        select.select_by_visible_text(year)
        
        # Input MSWA ID
        id_element = wd.find_element(By.XPATH, 
            "/html/body/center/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td[3]/input")
        id_element.clear()  # Clear any previous input
        id_element.send_keys(mswa_id)
        
        # Click Show button
        show_button = wd.find_element(By.XPATH, 
            "/html/body/center/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td[4]")
        show_button.click()
        
        time.sleep(0.2)  # Wait for page to update
        return True
        
    except NoSuchElementException as e:
        print(f"Element not found for swimmer {mswa_id}: {e}")
        return False
    except Exception as e:
        print(f"Error searching for swimmer {mswa_id}: {e}")
        return False

def extract_swimmer_data(wd):
    """
    Extract swimmer results from the current page.
    
    Returns:
        pd.DataFrame or None: DataFrame with results, or None if no data
    """
    try:
        # Get all table rows
        all_rows = wd.find_elements(By.XPATH, 
            "/html/body/center/table/tbody/tr/td/table[4]/tbody/tr")
        
        if not all_rows:
            print("No results table found")
            return None
        
        # Extract swimmer name from first row
        name_text = all_rows[0].text
        name_only = name_text.split("[")[0].strip()
        last, first = [part.strip() for part in name_only.split(",")]
        clean_name = f"{first} {last}"
        print(f"Currently processing {clean_name}")
        
        # Extract data rows (skip headers and empty rows)
        data = []
        for i, row in enumerate(all_rows):
            row_text = row.text.strip()
            
            # Skip if: first 3 rows, header rows (contain "Point:" or "MSA ID"), or empty
            if (i < 3 or 
                "Point:" in row_text or 
                "MSA ID" in row_text or 
                not row_text):
                continue
            
            cols = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
            
            # Only add rows with the expected number of columns (12)
            if len(cols) == 12:
                data.append(cols)
        
        if not data:
            print(f"No swim data found for {clean_name}")
            return None
        
        # Create DataFrame
        colnames = ["MSA ID", "Club", "Sex", "AgeGrp", "Course", "Distance", 
                    "Stroke", "Result", "Split", "Point", "Date", "Location"]
        df = pd.DataFrame(data, columns=colnames)
        df['Name'] = clean_name
        
        # Filter out zero-point swims
        df = df[df["Point"] != '0']
        
        # Debug: print if we filtered everything out
        if len(data) > 0 and len(df) == 0:
            print(f"  ⚠ Warning: All {len(data)} swims for {clean_name} were 0 points and filtered out")
        
        return df if len(df) > 0 else None
        
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None

def scrape_all_swimmers(mswa_ids, year, progress_callback=None):
    """
    Scrape results for multiple swimmers efficiently using a single browser instance.
    
    Args:
        mswa_ids: List or Series of MSWA ID numbers
        year: Year to search (e.g., "2025")
        progress_callback: Optional function to call with progress updates
        
    Returns:
        pd.DataFrame: Combined results for all swimmers
    """
    wd = setup_driver()
    all_results = []
    
    try:
        for idx, mswa_id in enumerate(mswa_ids):
            print(f"\nProcessing swimmer {idx+1}/{len(mswa_ids)}: {mswa_id}")
            
            # Search for swimmer
            if input_swimmer_search(wd, year, mswa_id):
                # Extract data
                swimmer_df = extract_swimmer_data(wd)
                
                if swimmer_df is not None:
                    all_results.append(swimmer_df)
                    print(f"  ✓ Found {len(swimmer_df)} results")
                else:
                    print(f"  ✗ No results for {mswa_id}")
            else:
                print(f"  ✗ Search failed for {mswa_id}")
            
            # Progress callback
            if progress_callback:
                progress_callback(idx + 1, len(mswa_ids))
            
            time.sleep(0.1)  # Brief delay between swimmers
            
    finally:
        wd.quit()
    
    # Combine all results
    if all_results:
        combined_df = pd.concat(all_results, ignore_index=True)
        print(f"\n✓ Successfully scraped {len(combined_df)} total results from {len(all_results)} swimmers")
        return combined_df
    else:
        print("\n✗ No results found for any swimmers")
        return pd.DataFrame()

# Example usage:
if __name__ == "__main__":
    # Load your Excel file
    df = pd.read_excel("swimmers.xlsx")
    
    # Scrape all results
    results_df = scrape_all_swimmers(
        mswa_ids=df["MSWA number"],
        year="2025"
    )
    
    # Save results
    if not results_df.empty:
        results_df.to_csv("swimming_results.csv", index=False)
        print(f"Results saved! Total rows: {len(results_df)}")

# Open the MSA Endurance 1000 Results page
# Old code removed by Claude

def setupdriver():
    url = "https://e1000.msarc.org.au/results/results.php"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    wd = webdriver.Chrome(options=options)
    wd.get(url)
    return wd

def driverinputswimmer(wd, year, MSWAID):
    # wd - output from wetupdriver
    # year of MSWA content (e.g. 2025)
    # MSWAID - MSWA ID number
    # # Selecting the correct year
    print('Starting with swimmer:', MSWAID)
    print(MSWAID)
    element1 = wd.find_element(By.XPATH, "/html/body/center/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td[1]/select") #By.NAME = year 
    select = Select(element1)
    try:
        select.select_by_visible_text(year)
    except:
        print('Invalid year, try again. Selected year: ', year)
        return None
    # Inputting the MSWA number
    element2 = wd.find_element(By.XPATH, "/html/body/center/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td[3]/input")
    element2.send_keys(MSWAID)
    # Clicking the Show button
    try:
        wd.find_element(By.XPATH, "/html/body/center/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td[4]").click()
        print('found')
        #print(wd)
        return wd
    except Exception as e:
        print("No swims completed by ", MSWAID, " in the ", year, " season. Error: ", e)
        return None

#html = wd.page_source #getting updated html generated by javascript

def swimmertodf(wd):
    if wd == None:
        print("Invalid selection or swimmer hasn't done any swims in the relevant season")
        return None
    else:
        print('this is being called!!')
        # wd - output from driverinputswimmer
        # Extract rows
        all_rows = wd.find_elements(By.XPATH, "/html/body/center/table/tbody/tr/td/table[4]/tbody/tr")
        #all_rows = wd.find_elements(By.XPATH, "/html/body/center/table/tbody/tr/td/table[4]/tbody")
        #all_rows = wd.find_elements(By.XPATH, "/html/body/center/table/tbody/tr/td/table[4]")
        if not all_rows: #if all rows is empty, it means there's no data to input
            print("Invalid selection or swimmer hasn't done any swims in the relevant season")
            return None
        else:
            # Extract data from non-header rows
            data = []
            rowskip = [0, 1, 2, 17, 18, 33, 34, 49, 50, 61, 62]
            for i, row in enumerate(all_rows):
                if i in rowskip:
                    if i == 0:
                        text = row.text #Finding name of the swimmer so it can be added to DF
                        name_only = text.split("[")[0].strip() #In the format HAINES , TEAGYN [ Point: 20 ]
                        last, first = [part.strip() for part in name_only.split(",")]
                        clean_name = f"{first} {last}"
                else:
                    cols = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
                    if cols:
                        data.append(cols)

            # Create DataFrame (pandas will assign default column names)
            colnames = ["MSA ID", "Club", "Sex", "AgeGrp", "Course", "Distance", "Stroke", "Result", "Split", "Point", "Date", "Location"]
            df = pd.DataFrame(data, columns=colnames)
            df['Name'] = clean_name
            df = df[df["Point"] !='0']
            return df

def get_swimmer_results(mswa_id, year):
    time.sleep(0.1)  # delay between requests
    wd = setupdriver()
    try:
        df = driverinputswimmer(wd, year, mswa_id)
        time.sleep(0.2)
        df = swimmertodf(df)
        return df
    finally:
        wd.quit()

def get_swimmer_quicker(wd, mswa_id, year):
    #time.sleep(0.1)  # delay between requests
    try:
        df = driverinputswimmer(wd, year, mswa_id)
        time.sleep(0.1)
        df = swimmertodf(df)
    except:
        wd.quit()
        wd = setupdriver()
        df = None
    return df, wd

def get_swimmer_results_quick(mswa_id, year):
    time.sleep(0.1)  # delay between requests
    wd = setupdriver()
    try:
        df = driverinputswimmer(wd, year, mswa_id)
        time.sleep(0.2)
        df = swimmertodf(df)
        return df
    finally:
        wd.quit()



#=setupdriver()
#print(a)
#b=driverinputswimmer(a, "2025", "444622")
#print(b)
#b=driverinputswimmer(a, "2025", "805709")
#c=swimmertodf(b)
#print(c)

#print(get_swimmer_results("444622", "2025"))
woah = ["MSWA number", "Name"]
data = [("444622", "Yvette"),
        ("802451", "Andrew"), 
         ("805709", "James")]
df=pd.DataFrame(data, columns = woah)
year = "2025"
#wd = setupdriver()
dfs = df["MSWA number"].apply(lambda x: get_swimmer_results(x, year))
# Drop None results (i.e., failed lookups)
dfs = dfs.dropna()
# Combine
final_df = pd.concat(dfs.tolist(), ignore_index=True)
print(final_df)

pio.renderers.default = 'browser'



HISTOGRAM WITH ALL SWIMMERS
fig = px.histogram(
        final_df,
        x = "Name",
        y = "Point",
        hover_name = "Name",
        color = "Stroke",
        histfunc="sum", 
        title="EM1000 Points per swimmer")

fig.update_traces(hovertemplate="<b>Name: %{x}</b>"+
                                 "<br>Points: %{y}")

fig.update_layout(
    yaxis=dict(title = dict(text = "Points")))

fig.show()

final_df["Date"] = pd.to_datetime(final_df["Date"], format='%d.%m.%Y')
final_df["Point"] = pd.to_numeric(final_df["Point"])
final_df = final_df.sort_values(["Name", "Date"])
final_df['Agg Points'] = final_df.groupby("Name")["Point"].cumsum()
print(final_df)
fig = px.line(
    final_df,
    x="Date",
    y="Agg Points",
    color="Name"
)

fig.show()
"""
'''
