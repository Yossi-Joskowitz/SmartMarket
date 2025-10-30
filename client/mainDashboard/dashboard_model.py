import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from inventory.inventory_presenter import create_inventory_page
from pricing.pricing_presenter import create_pricing_page
from Chat.chat_presenter import create_chat_page
from reports.reports_presenter import create_reports_page



class DashboardModel:
    """Model: owns external calls and page factories."""

    def __init__(self) -> None:
        # Cache for created pages to avoid recreating them
        self._inventory_page = None
        self._pricing_page = None
        self._reports_page = None
        self._chat_panel = None

    def build_inventory_page(self):
        if self._inventory_page is None:
            self._inventory_page = create_inventory_page()
        return self._inventory_page

    def build_pricing_page(self):
        if self._pricing_page is None:
            self._pricing_page = create_pricing_page()
        return self._pricing_page

    def build_reports_page(self):
        if self._reports_page is None:
            self._reports_page = create_reports_page()
        return self._reports_page

    def build_chat_panel(self):
        if self._chat_panel is None:
            self._chat_panel = create_chat_page()
        return self._chat_panel
    