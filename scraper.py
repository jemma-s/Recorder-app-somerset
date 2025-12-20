"""
Web scraping functions for MSWA Endurance 1000 results
This is your existing scraper code, cleaned up
"""
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException

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
        id_element.clear()
        id_element.send_keys(mswa_id)
        
        # Click Show button
        show_button = wd.find_element(By.XPATH, 
            "/html/body/center/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td[4]")
        show_button.click()
        
        time.sleep(0.2)
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
        all_rows = wd.find_elements(By.XPATH, 
            "/html/body/center/table/tbody/tr/td/table[4]/tbody/tr")
        
        if not all_rows:
            print("No results table found")
            return None
        
        # Extract swimmer name
        name_text = all_rows[0].text
        name_only = name_text.split("[")[0].strip()
        last, first = [part.strip() for part in name_only.split(",")]
        clean_name = f"{first} {last}"
        print(f"Currently processing {clean_name}")
        
        # Extract data rows
        data = []
        for i, row in enumerate(all_rows):
            row_text = row.text.strip()
            
            if (i < 3 or 
                "Point:" in row_text or 
                "MSA ID" in row_text or 
                not row_text):
                continue
            
            cols = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
            
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
            
            if input_swimmer_search(wd, year, mswa_id):
                swimmer_df = extract_swimmer_data(wd)
                
                if swimmer_df is not None:
                    all_results.append(swimmer_df)
                    print(f"  ✓ Found {len(swimmer_df)} results")
                else:
                    print(f"  ✗ No results for {mswa_id}")
            else:
                print(f"  ✗ Search failed for {mswa_id}")
            
            if progress_callback:
                progress_callback(idx + 1, len(mswa_ids))
            
            time.sleep(0.1)
            
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