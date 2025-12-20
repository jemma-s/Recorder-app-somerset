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

# Create singleton instance
data_store = DataStore()