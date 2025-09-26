
import random
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame ,QLabel, QPushButton, QLineEdit, QSplitter, QStackedWidget, QGridLayout, QTextEdit
from PySide6.QtCore import Qt
from datetime import datetime

from AgentCard import AgentCard
from DetailedPanel import DetailedPanel
from presenter.inventory_presenter import create_inventory_page



class MainDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SuperMarket AI agent")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Agent colors
        self.agent_colors = {
            "Inventory": "#007ACC",
            "Market": "#00AA00", 
            "Pricing": "#FF8C00",
            "Procurement": "#9966CC",
            "Manager": "#C0C0C0"
        }
        
        self.setupUI()
        self.apply_dark_theme()
        
    def setupUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top navbar
        self.create_navbar()
        
        # Content area with sidebar
        self.content_layout = QSplitter(Qt.Horizontal)
        
        # Left sidebar
        self.create_sidebar()
        
        # Main content with bottom panel
        self.main_splitter = QSplitter(Qt.Vertical)
        
        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        
        # Dashboard view (default)
        self.dashboard_view = self.create_dashboard_view()
        self.stacked_widget.addWidget(self.dashboard_view)
        
        # Inventory view 
        self.inventory_page = create_inventory_page()  
        self.stacked_widget.addWidget(self.inventory_page)

        # Procurement view
        self.procurement_page = create_inventory_page(parent=self)  # Placeholder, replace with actual
        self.stacked_widget.addWidget(self.procurement_page)
        
        
        # Detailed panel
        self.detailed_panel = DetailedPanel()
        self.stacked_widget.addWidget(self.detailed_panel)
        
        # Bottom panel for logs
        self.bottom_panel = self.create_bottom_panel()
        
        self.main_splitter.addWidget(self.stacked_widget)
        self.main_splitter.addWidget(self.bottom_panel)
        self.main_splitter.setSizes([600, 200])
        
        self.content_layout.addWidget(self.sidebar)
        self.content_layout.addWidget(self.main_splitter)
        self.content_layout.setSizes([200, 1200])
        
        main_layout.addWidget(self.navbar)
        main_layout.addWidget(self.content_layout)
        
        central_widget.setLayout(main_layout)
        
    def create_navbar(self):
        self.navbar = QFrame()
        self.navbar.setFixedHeight(60)
        self.navbar.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border-bottom: 2px solid #444444;
            }
        """)
        
        navbar_layout = QHBoxLayout()
        navbar_layout.setContentsMargins(20, 10, 20, 10)
        
        # Logo/Title
        logo = QLabel("🤖 AI Agents")
        logo.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        
        # Search bar
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search...")
        search_bar.setFixedWidth(300)
        search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E1E;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 8px 12px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #007ACC;
            }
            QLineEdit:hover {
                border: 2px solid #007ACC;
            }
        """)
        
        # Right side buttons
        notifications = QPushButton("🔔")
        notifications.setFixedSize(40, 40)
        notifications.setStyleSheet("""
            QPushButton {
                background-color: #3C3C3C;
                border: none;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4C4C4C;
            }
        """)
        
        profile = QPushButton("👤")
        profile.setFixedSize(40, 40)
        profile.setStyleSheet(notifications.styleSheet())
        
        navbar_layout.addWidget(logo)
        navbar_layout.addStretch()
        navbar_layout.addWidget(search_bar)
        navbar_layout.addStretch()
        navbar_layout.addWidget(notifications)
        navbar_layout.addWidget(profile)
        
        self.navbar.setLayout(navbar_layout)
        
    def create_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-right: 2px solid #444444;
            }
        """)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(5)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        
        # Menu buttons
        menu_items = [
            ("🤖", "Agents"),
            ("📦", "Inventory"), 
            ("📈", "Market"),
            ("💰", "Pricing"),
            ("🛒", "Procurement"),
            ("👨‍💼", "Manager"),
            ("📋", "Reports")
        ]
        
        for icon, text in menu_items:
            btn = QPushButton(f"{icon} {text}")
            btn.setFixedHeight(45)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2B2B2B;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    text-align: left;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #3C3C3C;
                }
                QPushButton:pressed {
                    background-color: #007ACC;
                }
            """)
            if text == "Agents":
                btn.clicked.connect(self.show_dashboard)
            elif text == "Inventory":
                btn.clicked.connect(self.show_inventory)
            elif text == "Procurement":
                btn.clicked.connect(self.show_procurement)
            sidebar_layout.addWidget(btn)
            
        sidebar_layout.addStretch()
        self.sidebar.setLayout(sidebar_layout)
        
    def create_dashboard_view(self):
        dashboard = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Agent Overview")
        title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
            }
        """)
        
        # Grid of agent cards
        grid_widget = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create agent cards
        agents = [
            # ("Inventory", "📦", "Stockouts ↓ 15%"),
            ("Market", "📈", "Growth ↑ 8%"),
            ("Pricing", "💰", "Margin ↑ 3.2%"),
            ("Procurement", "🛒", "Cost ↓ 7%"),
            ("Manager", "👨‍💼", "Efficiency ↑ 12%")
        ]
        
        for i, (name, icon, kpi) in enumerate(agents):
            card = AgentCard(
                name, icon, 
                self.agent_colors[name],
                status=random.choice(["active", "warning", "active"]),
                kpi=kpi
            )
            card.cardClicked.connect(self.show_agent_details)
            
            row = i // 2
            col = i % 2
            grid_layout.addWidget(card, row, col)
            
        grid_widget.setLayout(grid_layout)
        
        layout.addWidget(title)
        layout.addWidget(grid_widget)
        layout.addStretch()
        
        dashboard.setLayout(layout)
        return dashboard
        
    def create_bottom_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border-top: 2px solid #444444;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Header
        header = QLabel("🔍 AI Decision Explainability & Logs")
        header.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        
        # Add sample logs
        sample_logs = [
            "[2024-01-15 14:30] Inventory Agent: Detected low stock for Widget A (150 units)",
            "[2024-01-15 14:31] Pricing Agent: Recommending 10% price increase for Widget A due to low supply",
            "[2024-01-15 14:32] Market Agent: Competitor analysis shows opportunity for price adjustment",
            "[2024-01-15 14:33] Manager Agent: Coordinating response between Inventory and Pricing agents",
            "[2024-01-15 14:34] Procurement Agent: Initiating emergency restock order from Supplier A"
        ]
        
        self.log_text.setPlainText("\n".join(sample_logs))
        
        layout.addWidget(header)
        layout.addWidget(self.log_text)
        
        panel.setLayout(layout)
        return panel
        
    def show_dashboard(self):
        self.stacked_widget.setCurrentIndex(0)
        
    def show_inventory(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_procurement(self):
        self.stacked_widget.setCurrentIndex(3)

    def show_agent_details(self, agent_name):
        color = self.agent_colors[agent_name]
        self.detailed_panel.show_agent_details(agent_name, color)
        self.stacked_widget.setCurrentIndex(2)
        
        # Add log entry
        current_logs = self.log_text.toPlainText()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_log = f"[{timestamp}] User opened {agent_name} Agent detailed view"
        self.log_text.setPlainText(current_logs + "\n" + new_log)
        
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QSplitter::handle {
                background-color: #444444;
            }
        """)
    
    