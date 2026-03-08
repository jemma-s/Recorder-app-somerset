"""
Shared data storage accessible across all tabs
"""
import pandas as pd

class DataStore:
    """Singleton class to store shared data across tabs"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataStore, cls).__new__(cls)
            cls._instance.members_df = None  # Original uploaded data
            cls._instance.results_df = None   # Scraped results
            cls._instance.selected_members_other_club_df = None   # Overall data from other_club_members tab
            cls._instance.selected_club = None   # Selected club from other_club_members tab
            cls._instance.results_other_club_df = None
        return cls._instance
    
    def set_members_data(self, df):
        """Store the uploaded swimmers DataFrame"""
        self.members_df = df
    
    def get_members_data(self):
        """Retrieve the swimmers DataFrame"""
        return self.members_df
    
    def set_results_data(self, df):
        """Store the scraped results DataFrame"""
        self.results_df = df
    
    def get_results_data(self):
        """Retrieve the results DataFrame"""
        return self.results_df
    
    def has_members_data(self):
        """Check if swimmers data exists"""
        return self.members_df is not None and not self.members_df.empty
    
    def has_results_data(self):
        """Check if results data exists"""
        return self.results_df is not None and not self.results_df.empty
 
    def set_results_selected_members_other_club_df(self, df):
        """Store the overall DataFrame from other_club_members.py"""
        self.selected_members_other_club_df = df
    
    def get_results_selected_members_other_club_df(self):
        """Store the overall DataFrame from other_club_members.py"""
        return self.selected_members_other_club_df
    
    def has_results_selected_members_other_club_df(self):
        """Store the overall DataFrame from other_club_members.py"""
        return self.selected_members_other_club_df is not None and not self.selected_members_other_club_df.empty
    
    def set_selected_club(self, club):
        """Store the selected club from other_club_members.py"""
        self.selected_club = club
    
    def get_selected_club(self):
        """Store the selected club from other_club_members.py"""
        return self.selected_club
    
    def has_selected_club(self):
        """Store the selected club from other_club_members.py"""
        return self.selected_club is not None
    
    def set_results_other_club_data(self, df):
        """Store the scraped results DataFrame from scrape_other_club_members"""
        self.results_other_club_df = df
    
    def get_results_other_club_data(self):
        """Retrieve the results DataFrame from scrape_other_club_members"""
        return self.results_other_club_df
    
    def has_results_other_club_data(self):
        """Check if results exist from scrape_other_club_members"""
        return self.results_other_club_df is not None and not self.results_other_club_df.empty
    
    def get_member_name(self, mswa_id):
        #Get member name from MSWA ID
        if not self.has_members_data():
            return "Unknown"
    
        try:
            member_row = self.members_df[self.members_df["MSWA number"] == mswa_id]
            if len(member_row) > 0:
                if "First name" in self.members_df.columns and "Surname" in self.members_df.columns:
                    first = member_row["First name"].iloc[0]
                    last = member_row["Surname"].iloc[0]
                    return f"{first} {last}"
        except:
            pass
    
        return "Unknown"
    
    def get_selected_club_member_name(self, mswa_id):
        #Get member name from MSWA ID
        if not self.has_results_selected_members_other_club_df():
            return "Unknown"
    
        try:
            member_row = self.selected_members_other_club_df[self.selected_members_other_club_df["ID"] == mswa_id]
            if len(member_row) > 0:
                if "Name" in self.selected_members_other_club_df.columns:
                    name = member_row["Name"].iloc[0]
                    return f"{name}"
        except:
            pass
    
        return "Unknown"

# Create singleton instance
data_store = DataStore()