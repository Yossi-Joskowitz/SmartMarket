import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from typing import Dict, Optional
from PySide6.QtWidgets import QMessageBox

from .dashboard_view import MainDashboardView
from .dashboard_model import DashboardModel


class MainDashboardPresenter:
    def __init__(self, view: MainDashboardView, model: DashboardModel, user_info: Optional[Dict[str, str]] = None) -> None:
        self.view = view
        self.model = model
        self.user_info = user_info

        # Set user info in the view
        if user_info:
            self.view.set_user_info(user_info)

        # Set chat as the default page when app opens
        self.view.set_current_page(self.model.build_chat_panel())

        # Wire signals from the View
        self.view.inventoryClicked.connect(self.on_inventory)
        self.view.pricingClicked.connect(self.on_pricing)
        self.view.reportsClicked.connect(self.on_reports)
        self.view.chatClicked.connect(self.on_chat)
        self.view.userManagementClicked.connect(self.on_user_management)
        self.view.logoutRequested.connect(self.on_logout)

    def on_inventory(self) -> None:
        self.view.set_current_page(self.model.build_inventory_page())

    def on_pricing(self) -> None:
        self.view.set_current_page(self.model.build_pricing_page())

    def on_reports(self) -> None:
        self.view.set_current_page(self.model.build_reports_page())

    def on_chat(self) -> None:
        self.view.set_current_page(self.model.build_chat_panel())

    def on_user_management(self) -> None:
        """Handle user management page request"""
        self.view.set_current_page(self.model.build_user_management_page())

    def on_logout(self) -> None:
        """Handle logout by asking for confirmation and closing the main window."""
        reply = QMessageBox.question(
            self.view,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.view.close()


def create_main_dashboard(user_info: Optional[Dict[str, str]] = None) -> MainDashboardView:
    view = MainDashboardView()
    model = DashboardModel()
    view.presenter = MainDashboardPresenter(view, model, user_info)
    return view
