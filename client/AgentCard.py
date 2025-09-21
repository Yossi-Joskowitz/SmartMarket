from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal



class AgentCard(QFrame):
    cardClicked = Signal(str)
    
    def __init__(self, name, icon, color, status="active", kpi=""):
        super().__init__()
        self.agent_name = name
        self.color = color
        self.setupUI(name, icon, status, kpi)
        
    def setupUI(self, name, icon, status, kpi):
        self.setFixedSize(280, 160)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2B2B2B;
                border: 2px solid {self.color};
                border-radius: 12px;
                margin: 10px;
            }}
            QFrame:hover {{
                border: 3px solid {self.color};
                background-color: #333333;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                font-size: 24px;
                font-weight: bold;
                border: 1px ;
            }}
        """)
        
        title_label = QLabel(name)
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 20px;
                font-weight: bold;
                border: 1px ;
            }
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Status indicator
        status_colors = {"active": "#00FF00", "warning": "#FFA500", "error": "#FF0000"}
        status_label = QLabel("●")
        status_label.setStyleSheet(f"""
            QLabel {{
                color: {status_colors.get(status, "#00FF00")};
                font-size: 20px;
                border: 1px ;
                
            }}
        """)
        header_layout.addWidget(status_label)
        
        # KPI
        kpi_label = QLabel(kpi)
        kpi_label.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                font-size: 14px;
                margin-top: 10px;
            }
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(kpi_label)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.cardClicked.emit(self.agent_name)
        