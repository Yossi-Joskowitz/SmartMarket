from PySide6.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np



class ChartWidget(QWidget):
    def __init__(self, agent_name, color):
        super().__init__()
        self.agent_name = agent_name
        self.color = color
        self.setupUI()
        
    def setupUI(self):
        layout = QVBoxLayout()
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 6), facecolor='#2B2B2B')
        self.canvas = FigureCanvas(self.figure)
        
        # Generate sample data based on agent type
        self.plot_data()
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def plot_data(self):
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#1E1E1E')
        
        # Generate sample data
        x = np.linspace(0, 10, 50)
        if self.agent_name == "Inventory":
            y = 100 + 20 * np.sin(x) + np.random.normal(0, 5, 50)
            ax.set_title("Inventory Levels", color='white', fontsize=14)
            ax.set_ylabel("Stock Level", color='white')
        elif self.agent_name == "Market":
            y = 50 + 30 * np.cos(x) + np.random.normal(0, 8, 50)
            ax.set_title("Market Trends", color='white', fontsize=14)
            ax.set_ylabel("Market Index", color='white')
        elif self.agent_name == "Pricing":
            y = 25 + 15 * np.sin(2*x) + np.random.normal(0, 3, 50)
            ax.set_title("Price Optimization", color='white', fontsize=14)
            ax.set_ylabel("Price ($)", color='white')
        elif self.agent_name == "Procurement":
            y = 75 + 25 * np.cos(0.5*x) + np.random.normal(0, 6, 50)
            ax.set_title("Procurement Efficiency", color='white', fontsize=14)
            ax.set_ylabel("Efficiency %", color='white')
        else:  # Manager
            y = 85 + 10 * np.sin(1.5*x) + np.random.normal(0, 4, 50)
            ax.set_title("Overall Performance", color='white', fontsize=14)
            ax.set_ylabel("Performance Score", color='white')
            
        ax.plot(x, y, color=self.color, linewidth=2)
        ax.grid(True, alpha=0.3)
        ax.tick_params(colors='white')
        ax.set_xlabel("Time", color='white')
        
        self.figure.tight_layout()
