from typing import Optional, List, Dict
import os
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QLineEdit, QSplitter, QMenu, QWidgetAction, QListWidget, QListWidgetItem,
    QGraphicsDropShadowEffect, QStackedWidget
)
from PySide6.QtGui import QColor, QIcon
from theme_manager import ThemeManager


class MainDashboardView(QMainWindow):
    # Signals emitted when the user interacts with the sidebar
    inventoryClicked = Signal()
    pricingClicked   = Signal()
    reportsClicked   = Signal()
    managerClicked   = Signal()
    chatClicked      = Signal()  # New signal for chat
    userManagementClicked = Signal()  # New signal for user management
    logoutRequested  = Signal()  # Signal for logout

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SuperMarket AI agent")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Set window icon
        self._set_window_icon()

        # Core widgets
        self.navbar: Optional[QFrame] = None
        self.sidebar: Optional[QFrame] = None
        self.content_layout: Optional[QSplitter] = None
        self.main_splitter: Optional[QSplitter] = None
        self.stacked_widget: Optional[QStackedWidget] = None
        self.current_page: Optional[QWidget] = None
        self._sidebar_buttons: List[QPushButton] = []

        self._current_popover: Optional[QMenu] = None  # keep popover alive
        self.user_info: Optional[Dict[str, str]] = None  # Store user information

        self._build_ui()

    def set_current_page(self, page: QWidget) -> None:
        # Check if the page is already in the stack
        for i in range(self.stacked_widget.count()):
            if self.stacked_widget.widget(i) == page:
                # Page already exists, just switch to it
                self.stacked_widget.setCurrentWidget(page)
                self.current_page = page
                return
        
        # Page doesn't exist yet, add it to the stack
        self.stacked_widget.addWidget(page)
        self.stacked_widget.setCurrentWidget(page)
        self.main_splitter.setSizes([600, 200])
        self.current_page = page

    def set_user_info(self, user_info: Dict[str, str]) -> None:
        """Set the user information to display in the profile."""
        self.user_info = user_info

    def _set_window_icon(self) -> None:
        """Set the window icon from logo.png file."""
        # Get the directory of the current file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to the client directory where logo.png is located
        logo_path = os.path.join(script_dir, "..", "logo.png")
        
        # Normalize the path to handle relative path properly
        logo_path = os.path.normpath(logo_path)
        
        if os.path.exists(logo_path):
            # Create QIcon from the logo file and set it as window icon
            icon = QIcon(logo_path)
            self.setWindowIcon(icon)
        else:
            # If logo.png is not found, try alternative paths
            alternative_paths = [
                os.path.join(script_dir, "logo.png"),  # Same directory as dashboard_view.py
                os.path.join(os.path.dirname(script_dir), "logo.png"),  # Client directory
                "logo.png"  # Current working directory
            ]
            
            for alt_path in alternative_paths:
                if os.path.exists(alt_path):
                    icon = QIcon(alt_path)
                    self.setWindowIcon(icon)
                    break

    # ---------- Build UI ----------
    def _build_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.navbar = self._create_navbar()
        self.content_layout = QSplitter(Qt.Horizontal)
        self.sidebar = self._create_sidebar()
        self.main_splitter = QSplitter(Qt.Vertical)
        
        # Use QStackedWidget to manage multiple pages without destroying them
        self.stacked_widget = QStackedWidget()
        self.current_page = QWidget()
        self.stacked_widget.addWidget(self.current_page)

        self.main_splitter.addWidget(self.stacked_widget)
        self.content_layout.addWidget(self.sidebar)
        self.content_layout.addWidget(self.main_splitter)
        self.content_layout.setSizes([200, 1200])

        main_layout.addWidget(self.navbar)
        main_layout.addWidget(self.content_layout)
        central_widget.setLayout(main_layout)

    def _create_navbar(self) -> QFrame:
        navbar = QFrame()
        navbar.setFixedHeight(60)
        navbar.setObjectName("Navbar")

        navbar_layout = QHBoxLayout()
        navbar_layout.setContentsMargins(20, 10, 20, 10)

        logo = QLabel("🤖 Smart Market")

        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search...")
        search_bar.setFixedWidth(300)

        def round_btn(text: str) -> QPushButton:
            btn = QPushButton(text)
            btn.setProperty("variant", "round")
            btn.setFixedSize(40, 40)
            return btn

        notifications = round_btn("🔔")
        profile = round_btn("👤")

        navbar_layout.addWidget(logo)
        navbar_layout.addStretch()
        navbar_layout.addWidget(search_bar)
        navbar_layout.addStretch()
        navbar_layout.addWidget(notifications)
        navbar_layout.addWidget(profile)

        navbar.setLayout(navbar_layout)

        notifications.clicked.connect(lambda: self._show_notifications_popover(notifications))
        profile.clicked.connect(lambda: self._show_profile_popover(profile))

        return navbar

    def _create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(5)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)

        menu_items = [
            ("📦", "Inventory", self.inventoryClicked),
            ("🛍️", "Product",   self.pricingClicked),
            ("📋", "Reports",   self.reportsClicked),
            ("💬", "Chat",      self.chatClicked),
        ]

        for icon, text, signal in menu_items:
            btn = QPushButton(f"{icon} {text}")
            btn.setFixedHeight(45)
            btn.setStyleSheet("text-align: left;")  
            btn.setToolTip(f"wait after click for {text} page to load")
            btn.clicked.connect(signal.emit)
            self._sidebar_buttons.append(btn)
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch()
        sidebar.setLayout(sidebar_layout)
        return sidebar

    def _make_popover(self, anchor_btn: QPushButton, content_widget, width: int = 320, height: int = 260) -> QMenu:
        # Close any existing popover to avoid overlaps and keep a strong reference
        if getattr(self, "_current_popover", None) and self._current_popover.isVisible():
            self._current_popover.close()

        menu = QMenu(self)
        content_widget.setFixedSize(width, height)

        # Soft drop shadow
        shadow = QGraphicsDropShadowEffect(menu)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 180 if ThemeManager.instance().theme == "dark" else 80))
        content_widget.setGraphicsEffect(shadow)

        act = QWidgetAction(menu)
        act.setDefaultWidget(content_widget)
        menu.addAction(act)

        # Keep reference so the menu is not garbage-collected while visible
        self._current_popover = menu
        menu.aboutToHide.connect(lambda: setattr(self, "_current_popover", None))

        btn_pos = anchor_btn.mapToGlobal(QPoint(0, anchor_btn.height()))
        menu.popup(btn_pos)
        return menu

    # -------- Notifications Popover --------
    def _show_notifications_popover(self, btn: QPushButton) -> None:
        widget = QFrame()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("Notifications")

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)

        list_widget = QListWidget()

        for txt in [
            "Low stock in dairy section (3 items)",
            "Coffee sales dropped 12%",
            "Snacks promotion ends today"
        ]:
            QListWidgetItem(txt, list_widget)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(8)

        mark_read = QPushButton("Mark as Read")
        refresh = QPushButton("Refresh")

        btn_row.addWidget(mark_read)
        btn_row.addStretch()
        btn_row.addWidget(refresh)

        layout.addWidget(title)
        layout.addWidget(sep)
        layout.addWidget(list_widget, 1)
        layout.addLayout(btn_row)

        mark_read.clicked.connect(lambda: list_widget.clear())
        refresh.clicked.connect(lambda: print("Refreshing notifications..."))

        self._make_popover(btn, widget, width=340, height=280)

    # -------- Profile Popover --------
    def _show_profile_popover(self, btn: QPushButton) -> None:
        widget = QFrame()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Use actual user info if available, otherwise use default
        if self.user_info:
            display_name = self.user_info.get('display_name', 'User')
            email = self.user_info.get('email', 'user@example.com')
            name_text = f"👤 {display_name}"
            role_text = f"{email} • SmartMarket"
        else:
            name_text = "👤 Admin User"
            role_text = "Manager • SmartMarket"

        name = QLabel(name_text)
        role = QLabel(role_text)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)

        row1 = QHBoxLayout()
        row1.setSpacing(8)


        # Toggle theme button
        toggle = QPushButton("Switch to Light Mode" if ThemeManager.instance().theme == "dark" else "Switch to Dark Mode")
        toggle.clicked.connect(lambda: (ThemeManager.instance().toggle(QApplication.instance()),
                                        toggle.setText("Switch to Light Mode" if ThemeManager.instance().theme == "dark" else "Switch to Dark Mode")))

        logout = QPushButton("Logout")
        logout.setProperty("variant", "danger")

        toggle.setFixedHeight(toggle.sizeHint().height())
        logout.setFixedHeight(logout.sizeHint().height())
        layout.addWidget(name)
        layout.addWidget(role)
        layout.addWidget(sep)
        layout.addLayout(row1)
        layout.addSpacing(6)
        layout.addWidget(toggle)
        layout.addSpacing(6)
        layout.addWidget(logout)

        logout.clicked.connect(self.logoutRequested.emit)

        self._make_popover(btn, widget, width=280, height=220)

