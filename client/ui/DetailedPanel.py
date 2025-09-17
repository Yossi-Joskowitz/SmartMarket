from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QSplitter
from PySide6.QtCore import Qt

from ChartWidget import ChartWidget


class DetailedPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.current_agent = None
        self.setupUI()
        
    def setupUI(self):
        self.main_layout = QVBoxLayout()
        
        # Header
        self.header = QLabel("Select an agent to view details")
        self.header.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 20px;
                font-weight: bold;
                padding: 20px;
                background-color: #2B2B2B;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        
        # Content area with splitter
        self.content_splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Chart
        self.chart_container = QWidget()
        self.chart_layout = QVBoxLayout()
        self.chart_container.setLayout(self.chart_layout)
        
        # Right side - Table and buttons
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout()
        
        # Data table
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2B2B2B;
                color: #FFFFFF;
                gridline-color: #444444;
                border: 1px solid #444444;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #3C3C3C;
                color: #FFFFFF;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.approve_btn = QPushButton("✓ Approve")
        self.approve_btn.setStyleSheet("""
            QPushButton {
                background-color: #00AA00;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00CC00;
            }
        """)
        
        self.reject_btn = QPushButton("✗ Reject")
        self.reject_btn.setStyleSheet("""
            QPushButton {
                background-color: #CC0000;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF0000;
            }
        """)
        
        button_layout.addWidget(self.approve_btn)
        button_layout.addWidget(self.reject_btn)
        button_layout.addStretch()
        
        self.right_layout.addWidget(self.table)
        self.right_layout.addLayout(button_layout)
        self.right_container.setLayout(self.right_layout)
        
        # Add to splitter
        self.content_splitter.addWidget(self.chart_container)
        self.content_splitter.addWidget(self.right_container)
        self.content_splitter.setSizes([600, 400])
        
        self.main_layout.addWidget(self.header)
        self.main_layout.addWidget(self.content_splitter)
        
        self.setLayout(self.main_layout)
        
    def show_agent_details(self, agent_name, color):
        self.current_agent = agent_name
        self.header.setText(f"{agent_name} Agent Details")
        
        # Clear previous chart
        for i in reversed(range(self.chart_layout.count())):
            self.chart_layout.itemAt(i).widget().setParent(None)
            
        # Add new chart
        chart = ChartWidget(agent_name, color)
        self.chart_layout.addWidget(chart)
        
        # Update table data
        self.update_table_data(agent_name)
        
    def update_table_data(self, agent_name):
        # Sample data for different agents
        if agent_name == "Inventory":
            headers = ["Product", "SKU", "Current Stock", "Forecast", "Status"]
            data = [
                ["Widget A", "WA001", "150", "200", "Low"],
                ["Widget B", "WB002", "300", "250", "Optimal"],
                ["Widget C", "WC003", "50", "180", "Critical"],
                ["Widget D", "WD004", "220", "200", "Optimal"],
            ]
        elif agent_name == "Market":
            headers = ["Market", "Trend", "Competition", "Opportunity", "Risk"]
            data = [
                ["North America", "↑ Growing", "High", "Medium", "Low"],
                ["Europe", "→ Stable", "Medium", "High", "Medium"],
                ["Asia Pacific", "↑ Expanding", "Low", "High", "Medium"],
                ["Latin America", "↓ Declining", "Medium", "Low", "High"],
            ]
        elif agent_name == "Pricing":
            headers = ["Product", "Current Price", "Suggested Price", "Margin", "Action"]
            data = [
                ["Widget A", "$25.00", "$27.50", "22%", "Increase"],
                ["Widget B", "$30.00", "$28.00", "18%", "Decrease"],
                ["Widget C", "$45.00", "$47.00", "25%", "Increase"],
                ["Widget D", "$20.00", "$20.00", "20%", "Maintain"],
            ]
        elif agent_name == "Procurement":
            headers = ["Supplier", "Lead Time", "Cost", "Quality", "Reliability"]
            data = [
                ["Supplier A", "7 days", "$15.00", "95%", "High"],
                ["Supplier B", "14 days", "$12.50", "88%", "Medium"],
                ["Supplier C", "10 days", "$13.75", "92%", "High"],
                ["Supplier D", "21 days", "$11.00", "85%", "Low"],
            ]
        else:  # Manager
            headers = ["Agent", "Performance", "Efficiency", "Accuracy", "Status"]
            data = [
                ["Inventory", "92%", "88%", "95%", "Active"],
                ["Market", "87%", "91%", "89%", "Active"],
                ["Pricing", "94%", "85%", "92%", "Active"],
                ["Procurement", "89%", "93%", "87%", "Warning"],
            ]
            
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        for row, row_data in enumerate(data):
            for col, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                self.table.setItem(row, col, item)
                
        self.table.resizeColumnsToContents()
