#installing dependencies
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def memberslist(file):
    #Importing excel file with list of Somerset Masters Members
    members = pd.read_excel(file, header=None, skiprows=0) #Ensuring first row is counted as a member
    members.columns=['Firstname', 'Lastname', 'Age', 'Birthdate', 'Gender']
    return members

def websiteurl(firstname, lastname, aussieid, year):
    aussieid = str(aussieid)
    year = str(year)
    #url = "https://portal.msarc.org.au/results/results.php?year="+year+"&name=&aussiid="+aussieid+"&pb=no&sort=agegrp&Show=Show&js=on"
    url = "https://portal.msarc.org.au/results/results.php?year="+year+"&name="+firstname+"+"+lastname+"&aussiid=&pb=no&sort=agegrp&Show=Show&js=on"
    return url


def meets_list_from_url(year, state = "WA"):
    # Getting the list of meets in a year from a url
    # Obtains the URL for the website which contains the list of swim meets
    # Note: for 'National' option, state = "---"
    if state == "National":
        state = "---"
    year = str(year)
    url = "https://portal.msarc.org.au/meets/index.php?scope=&state="+ state + "&year=" + year + "&Show=Show&js=on"
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser') #Getting the HTML
    # Find all links that contain EventId (these are the meet links)
    meet_links = soup.find_all('a', href=re.compile(r'EventId=\d+'))

    meet_data = []

    for link in meet_links:
        meet_name = link.get_text(strip=True)
        meet_url = link.get('href', '')
        
        # Get the parent <td>
        parent_td = link.find_parent('td')
        
        if parent_td:
            # Find the next 4 <td> siblings that follow this one
            siblings = []
            current = parent_td
            
            # Collect up to 4 following td elements
            for _ in range(4):
                current = current.find_next_sibling('td')
                if current:
                    siblings.append(current)
                else:
                    break
            
            # Only add if we found at least 4 siblings (course, state, location, date)
            if len(siblings) >= 4:
                course = siblings[0].get_text(strip=True)
                state = siblings[1].get_text(strip=True)
                location = siblings[2].get_text(strip=True)
                date = siblings[3].get_text(strip=True)
                
                # Validate that this looks like real data
                # Course should be LC or SC
                # State should be short (2-3 chars)
                # Date should match date pattern
                if course in ['LC', 'SC'] and len(state) <= 3 and re.search(r'\d{2}\.\d{2}\.\d{4}', date):
                    meet_data.append({
                        'Meet': meet_name,
                        'Course': course,
                        'State': state,
                        'Location': location,
                        'Date': date,
                        'URL': meet_url
                    })

    return(pd.DataFrame(meet_data))


def datafromwebsite(url, parsed, firstname, lastname):
    try:
        data = requests.get(url).text
        soup = BeautifulSoup(data, 'html.parser') #Getting the HTML
        alltables = soup.find_all('table')
        table1 = alltables[8]
        # Find all table rows
        rows = table1.find_all('tr') #tr = table rows
        data = []
        for row in rows:
            # Get all <td> tags in the row
            cells = row.find_all('td') #td = a cell inside the row
            if len(cells) >= 13:  # Data rows have at least 13 cells
                row_data = [cell.get_text(strip=True) for cell in cells]
                # Only keep rows with actual data, not separators like <hr/>
                if row_data[1].isdigit():  # MSA ID is numeric
                    data.append(row_data)
        # Now extract the required fields from each data row
        # Format: [MSA ID, Club, Sex, AgeGrp, Course, Distance, Stroke, Time, Points, Date, Location]
        for row in data:
            extracted = [
                firstname,
                lastname,
                row[1],  # MSA ID
                row[2],  # Club
                row[3],  # Sex
                row[4],  # Age Group
                row[5],  # Course
                row[6],  # Distance
                row[7],  # Stroke
                row[8],  # Time
                row[9],  # "^" if timed swim EM1000
                row[10], # Distance (EM1000^)
                row[11], # Points
                row[12], # Date
                row[13]  # Location
            ]
            parsed.append(extracted)
    except:
        print('no data')
    return parsed

def parsedtopandas(parsed):
    df = pd.DataFrame(parsed, columns=['First name', 
                                       'Last name', 
                                       'MSWA number', 
                                       'Club', 
                                       'Gender', 
                                       'AgeGrp', 
                                       'Course', 
                                       'Distance',
                                       'Stroke', 
                                       'Time',
                                       'EM1000', 
                                       'EM1000Dist', 
                                       'Points', 
                                       'Date', 
                                       'Location'
                                       ]
                        )
    #toconvert_dict = {'Points': float}
    #df = df.astype(toconvert_dict)
    df["Points"] = df["Points"].replace('', 0).astype(int) #this is applicable if we're keeping the EM1000 scores
    mask = df['EM1000Dist'].str.endswith('^') #identifying rows in EM1000Dist column which end in ^
    df.loc[mask, 'EM1000Dist'] = df.loc[mask, 'EM1000Dist'].str.rstrip('^') #Removing ^ from EM1000Dist column
    df.loc[mask, 'EM1000'] = df.loc[mask, 'EM1000'] + '^' #Adding ^ to the EM1000 distance rows
    df = df[df.EM1000 != '^'] #Removing all EM1000 scores
    # We're going to delete the EM1000 scores from the dataset - will deal with these later
    #mask = df['EM1000Dist'].str.endswith('^') #identifying rows which are splits (has * in the EM1000 column)
    df = df[df.EM1000 != '*'] #Removing all split rows
    df["Full name"] = df["First name"].str.cat(df["Last name"], sep=" ")
    return(df)

def uniquemeets(df):
    #Creating a subset of unique combinations of Locations and Dates (aka meets) to do further filtering
    #df - Dataframe with the swimming data
    uniquemeets = df[["Location","Date"]].drop_duplicates()
    print(uniquemeets)
    return uniquemeets
        

def summarystats(dataframe, groupedcol, valuecol, meetname = None, date= None, orderby = 'MySum', uniquemeets = None):
    #Dataframe - the pandas df
    #Groupedcol - the column that we want to be grouped by
    #Valuecol - the column with the value that we want a summary of
    #Meetname is the meet that we may want the sums to be of
    #uniquemeets - a subset of the data with unique meets created from FUNC uniquemeets
    if meetname == None:
        if isinstance(uniquemeets, pd.DataFrame):
            print(isinstance(uniquemeets, pd.DataFrame))
            print('grouped by meet!!')
            summarydata = dataframe.groupby(
                ['Location', 'Date', groupedcol]
                )[valuecol].agg(
                    MySum='sum', 
                    MyCount='count').sort_values(
                        by=['Location', 'Date', orderby],
                        ascending=[True, True, False])
            #summarydata = summarydata.sort_values(by=orderby, ascending=False)
        else:
            print(isinstance(uniquemeets, pd.DataFrame))
            print('Swimmer data for the whole year')
            summarydata = dataframe.groupby(groupedcol)[valuecol].agg(MySum='sum', MyCount='count')
            summarydata = summarydata.sort_values(by=orderby, ascending=False)

    else:
        if date == None:
            print('Printing results for ', meetname, ' ')
            summarydata = dataframe[(dataframe['Location'] == meetname)].groupby(groupedcol)[valuecol].agg(MySum='sum', MyCount='count')
            summarydata = summarydata.sort_values(by=orderby, ascending=False)
        else:
            print('Printing results for ', meetname, ' ', date)
            summarydata = dataframe[(dataframe['Location'] == meetname)&(dataframe['Date']==date)].groupby(groupedcol)[valuecol].agg(MySum='sum', MyCount='count')
            summarydata = summarydata.sort_values(by=orderby, ascending=False)
    return summarydata

def EM1000points(dataframe):

    return

def data_from_website_individual(url, firstname, lastname):
    # Returns a dataframe with the results of an individual swimmer
    try:
        parsed = []
        data = requests.get(url).text
        soup = BeautifulSoup(data, 'html.parser') #Getting the HTML
        alltables = soup.find_all('table')
        table1 = alltables[8]
        # Find all table rows
        rows = table1.find_all('tr') #tr = table rows
        data = []
        for row in rows:
            # Get all <td> tags in the row
            cells = row.find_all('td') #td = a cell inside the row
            if len(cells) >= 13:  # Data rows have at least 13 cells
                row_data = [cell.get_text(strip=True) for cell in cells]
                # Only keep rows with actual data, not separators like <hr/>
                if row_data[1].isdigit():  # MSA ID is numeric
                    data.append(row_data)
        # Now extract the required fields from each data row
        # Format: [MSA ID, Club, Sex, AgeGrp, Course, Distance, Stroke, Time, Points, Date, Location]
        for row in data:
            extracted = [
                firstname,
                lastname,
                row[1],  # MSA ID
                row[2],  # Club
                row[3],  # Sex
                row[4],  # Age Group
                row[5],  # Course
                row[6],  # Distance
                row[7],  # Stroke
                row[8],  # Time
                row[9],  # "^" if timed swim EM1000
                row[10], # Distance (EM1000^)
                row[11], # Points
                row[12], # Date
                row[13]  # Location
            ]
            parsed.append(extracted)
    except:
        print('no data')
    return parsed

def individual_swimmers_results(MSWA_id, year, firstname, lastname):
    # Finding the individual results of a swimmer in a year
    MSWA_id = str(MSWA_id)
    year = str(year)
    url = "https://portal.msarc.org.au/results/results.php?year="+year+"&name=&aussiid="+MSWA_id+"&pb=no&sort=agegrp&Show=Show&js=on"

    df = data_from_website_individual(url, firstname, lastname)

    df = parsedtopandas(df)
    return df

def all_swimmers_results(df, year, MSWA_id = "MSWA number", firstname = "First name", lastname = "Surname"):
    # Finding all results for the year
    # This will return a large df with all swimming results for the year
    # The optional items are in case the column names of the df change

    all_results = pd.DataFrame()

    for i, row in df.iterrows():
        MSWA_number = row["MSWA number"]
        first_name = row["First name"]
        last_name = row["Surname"]
        individual_results = individual_swimmers_results(MSWA_number, year, first_name, last_name)
        all_results = pd.concat([all_results, individual_results])
    return all_results

def all_swimmers_results_grouped_points(df, year):
    # This will find all results for the year and will sum it on a per swimmer basis

    all_results = all_swimmers_results(df, year)

    #print(all_results)

    grouped_results = all_results.groupby(['Full name']).agg(
        Total_points = ('Points', 'sum'),
        Total_events = ('Full name', 'count'),
        Total_meets = ('Date', 'nunique')
    ).reset_index()
    summarydata = grouped_results.sort_values(by="Total_points", ascending=False)
    return summarydata



