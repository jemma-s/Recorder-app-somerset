"""
Tabs package for E1000 PyQt6 Application
"""

from .upload_tab import UploadTab
from .scrape_tab import ScrapeTab
from .visualize_tab import VisualizeTab
from .report_tab import ReportTab
from .birthday_tab import BirthdayTab
from .meets_tab import MeetsTab

__all__ = ['UploadTab','ScrapeTab', 'VisualizeTab', 'ReportTab', 'BirthdayTab', 'MeetsTab']