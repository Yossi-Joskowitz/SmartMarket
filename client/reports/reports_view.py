from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QTabWidget, QLabel, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QProgressBar, QMessageBox, QFileDialog,
    QHeaderView, QSplitter, QFrame
)
from PySide6.QtCore import Qt, Signal

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from .reports_model import (
    SalesReport, InventoryReport, PerformanceMetrics,
)

# Import theme manager to detect theme changes
try:
    from ..theme_manager import ThemeManager
except ImportError:
    try:
        from theme_manager import ThemeManager
    except ImportError:
        ThemeManager = None


class ReportsView(QWidget):
    """
    Main reports interface providing comprehensive analytics and reporting.
    """
    # Signals for communication with presenter
    salesReportGenerated = Signal(object)  # SalesReport
    inventoryReportGenerated = Signal(object)  # InventoryReport
    performanceMetricsGenerated = Signal(object)  # PerformanceMetrics
    exportRequested = Signal(str, str)  # file_path, format_type
    errorOccurred = Signal(str)  # Error message
    loadingStatusChanged = Signal(bool)  # True when loading, False when complete
    
    def __init__(self):
        """
        Initialize reports view with UI components."""
        super().__init__()
        self.presenter = None
        self._setup_ui()
        # Connect to theme changes
        if ThemeManager:
            ThemeManager.instance().themeChanged.connect(self._on_theme_changed)
    
    def _setup_ui(self) -> None:
        """
        Create and arrange all UI components following theme manager styling.
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)
        
        # Header with title and controls
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)
        
        # Progress bar for loading indication
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Main content with tabs
        self.tab_widget = QTabWidget()
        self._create_tabs()
        main_layout.addWidget(self.tab_widget)
    
    def _create_header(self) -> QHBoxLayout:
        """
        Create header section with title and global controls.
        """
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("📋 Reports & Analytics")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Global controls
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setFixedHeight(32)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.setFixedHeight(32)
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setEnabled(False)  # Disabled until data is loaded
        
        header_layout.addWidget(self.refresh_btn)
        header_layout.addWidget(self.export_btn)
        
        return header_layout
    
    def _create_tabs(self) -> None:
        """
        Create tabbed interface for different report types.
        """
        # Sales Report Tab
        self.sales_tab = self._create_sales_tab()
        self.tab_widget.addTab(self.sales_tab, "📊 Sales")
        
        # Inventory Report Tab
        self.inventory_tab = self._create_inventory_tab()
        self.tab_widget.addTab(self.inventory_tab, "📦 Inventory")
        
        # Performance Metrics Tab
        self.performance_tab = self._create_performance_tab()
        self.tab_widget.addTab(self.performance_tab, "📈 Performance")
    
    def _create_sales_tab(self) -> QWidget:
        """
        Create sales report tab with metrics display.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Controls section
        controls_frame = QFrame()
        controls_frame.setFixedHeight(50)
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(12, 12, 12, 12)
        
        controls_label = QLabel("Sales Report")
        
        # Generate button
        self.sales_generate_btn = QPushButton("Generate Report")
        self.sales_generate_btn.setFixedHeight(32)
        self.sales_generate_btn.setCursor(Qt.PointingHandCursor)
        
        controls_layout.addWidget(controls_label)
        controls_layout.addStretch()
        controls_layout.addWidget(self.sales_generate_btn)
        
        layout.addWidget(controls_frame)
        
        # Results section with splitter
        results_splitter = QSplitter(Qt.Horizontal)
        
        # Summary metrics
        summary_frame = QFrame()
        summary_main_layout = QVBoxLayout(summary_frame)
        summary_main_layout.setContentsMargins(16, 16, 16, 16)
        summary_main_layout.setSpacing(12)
        
        # Add explanation section
        explanation_title = QLabel("📊 Sales Overview")
        explanation_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2196F3;")
        summary_main_layout.addWidget(explanation_title)
        
        explanation_text = QLabel(
            "This report analyzes your store's sales performance by examining all products "
            "with positive profit margins. The data comes directly from your product database "
            "and shows which items are contributing to your revenue."
        )
        explanation_text.setWordWrap(True)
        explanation_text.setStyleSheet("font-size: 11px; color: #666; margin-bottom: 10px;")
        summary_main_layout.addWidget(explanation_text)
        
        # Field explanations
        field_explanations = QLabel(
            "• Total Revenue: Sum of profits from all profitable products\n"
            "• Product Count: Number of products generating positive profit\n"
            "• Avg per Product: Average profit contribution per profitable item"
        )
        field_explanations.setWordWrap(True)
        field_explanations.setStyleSheet("font-size: 10px; color: #888; margin-bottom: 15px;")
        summary_main_layout.addWidget(field_explanations)
        
        summary_title = QLabel("Summary Metrics")
        summary_title.setStyleSheet("font-weight: bold; margin-top: 10px;")
        summary_main_layout.addWidget(summary_title)
        
        summary_layout = QFormLayout()
        
        self.sales_revenue_label = QLabel("₪0.00")
        self.sales_revenue_label.setToolTip("Total revenue from all products with positive profit")
        
        self.sales_transactions_label = QLabel("0")
        self.sales_transactions_label.setToolTip("Number of products with positive profit from the database")
        
        self.sales_avg_value_label = QLabel("₪0.00")
        self.sales_avg_value_label.setToolTip("Average revenue per product (Total Revenue ÷ Product Count)")
        
        summary_layout.addRow("Total Revenue:", self.sales_revenue_label)
        summary_layout.addRow("Product Count:", self.sales_transactions_label)
        summary_layout.addRow("Avg per Product:", self.sales_avg_value_label)
        
        summary_main_layout.addLayout(summary_layout)
        summary_main_layout.addStretch()  # Push content to top like performance tab
        
        # Set minimum width for better proportion
        summary_frame.setMinimumWidth(350)
        summary_frame.setMaximumWidth(450)  # Also set maximum to control size
        results_splitter.addWidget(summary_frame)
        
        # Detailed data table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(2)
        self.sales_table.setHorizontalHeaderLabels(["Product", "Revenue"])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sales_table.setMinimumWidth(500)  # Ensure table has good minimum width
        self.sales_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make table read-only
        
        # Add tooltips to show all products
        self.sales_table.horizontalHeaderItem(0).setToolTip("All products sorted by revenue")
        self.sales_table.horizontalHeaderItem(1).setToolTip("Total revenue per product")
        
        results_splitter.addWidget(self.sales_table)
        results_splitter.setSizes([400, 600])
        results_splitter.setStretchFactor(0, 2)  # Left panel gets 2 parts
        results_splitter.setStretchFactor(1, 3)  # Right panel gets 3 parts
        
        layout.addWidget(results_splitter)
        
        return tab
    
    def _create_inventory_tab(self) -> QWidget:
        """
        Create inventory analysis tab with stock metrics and alerts.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Controls section
        controls_frame = QFrame()
        controls_frame.setFixedHeight(50)
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(12, 12, 12, 12)
        
        controls_label = QLabel("Inventory Analysis")
        
        self.inventory_generate_btn = QPushButton("Generate Report")
        self.inventory_generate_btn.setFixedHeight(32)
        self.inventory_generate_btn.setCursor(Qt.PointingHandCursor)
        
        controls_layout.addWidget(controls_label)
        controls_layout.addStretch()
        controls_layout.addWidget(self.inventory_generate_btn)
        
        layout.addWidget(controls_frame)
        
        # Results section
        results_splitter = QSplitter(Qt.Horizontal)
        
        # Summary metrics
        summary_frame = QFrame()
        summary_main_layout = QVBoxLayout(summary_frame)
        summary_main_layout.setContentsMargins(16, 16, 16, 16)
        summary_main_layout.setSpacing(12)
        
        # Add explanation section
        explanation_title = QLabel("📦 Inventory Overview")
        explanation_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #FF9800;")
        summary_main_layout.addWidget(explanation_title)
        
        explanation_text = QLabel(
            "This report provides a comprehensive view of your inventory across all product "
            "categories. The data shows total quantities and monetary values based on your "
            "current stock levels and pricing information."
        )
        explanation_text.setWordWrap(True)
        explanation_text.setStyleSheet("font-size: 11px; color: #666; margin-bottom: 10px;")
        summary_main_layout.addWidget(explanation_text)
        
        # Field explanations
        field_explanations = QLabel(
            "• Total Products: Sum of all product quantities in inventory\n"
            "• Total Value: Combined monetary value of all inventory items"
        )
        field_explanations.setWordWrap(True)
        field_explanations.setStyleSheet("font-size: 10px; color: #888; margin-bottom: 15px;")
        summary_main_layout.addWidget(field_explanations)
        
        summary_title = QLabel("Inventory Health")
        summary_title.setStyleSheet("font-weight: bold; margin-top: 10px;")
        summary_main_layout.addWidget(summary_title)
        
        summary_layout = QFormLayout()
        
        self.inventory_total_products_label = QLabel("0")
        self.inventory_total_products_label.setToolTip("Total quantity of all products across all categories from the database")
        
        self.inventory_total_value_label = QLabel("₪0.00")
        self.inventory_total_value_label.setToolTip("Total monetary value of all inventory from category value API")
        
        summary_layout.addRow("Total Products:", self.inventory_total_products_label)
        summary_layout.addRow("Total Value:", self.inventory_total_value_label)
        
        summary_main_layout.addLayout(summary_layout)
        summary_main_layout.addStretch()  # Push content to top like performance tab
        
        # Set minimum width for better proportion  
        summary_frame.setMinimumWidth(350)
        summary_frame.setMaximumWidth(450)  # Also set maximum to control size
        results_splitter.addWidget(summary_frame)
        
        # Category breakdown table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(3)
        self.inventory_table.setHorizontalHeaderLabels(["Category", "Items", "Value"])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.inventory_table.setMinimumWidth(500)  # Ensure table has good minimum width
        self.inventory_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make table read-only
        
        results_splitter.addWidget(self.inventory_table)
        results_splitter.setSizes([400, 600])
        results_splitter.setStretchFactor(0, 2)  # Left panel gets 2 parts
        results_splitter.setStretchFactor(1, 3)  # Right panel gets 3 parts
        
        layout.addWidget(results_splitter)
        return tab
    
    def _create_performance_tab(self) -> QWidget:
        """
        Create performance metrics tab with KPIs dashboard and interactive charts. """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Controls section
        controls_frame = QFrame()
        controls_frame.setFixedHeight(50)
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(12, 12, 12, 12)
        
        controls_label = QLabel("Performance Dashboard")
        
        # Date range filter for chart
        date_range_label = QLabel("Show Last:")
        self.performance_date_range = QComboBox()
        self.performance_date_range.addItems([
            "3 Months", "6 Months", "12 Months", "24 Months", "All Data"
        ])
        self.performance_date_range.setCurrentText("12 Months")
        self.performance_date_range.setFixedHeight(32)
        
        self.performance_generate_btn = QPushButton("Generate Chart")
        self.performance_generate_btn.setFixedHeight(32)
        self.performance_generate_btn.setCursor(Qt.PointingHandCursor)
        
        controls_layout.addWidget(controls_label)
        controls_layout.addWidget(date_range_label)
        controls_layout.addWidget(self.performance_date_range)
        controls_layout.addStretch()
        controls_layout.addWidget(self.performance_generate_btn)
        
        layout.addWidget(controls_frame)
        
        # Add explanation section above chart
        explanation_frame = QFrame()
        explanation_layout = QVBoxLayout(explanation_frame)
        explanation_layout.setContentsMargins(16, 16, 16, 10)
        
        explanation_title = QLabel("📈 Revenue & Profit Trends")
        explanation_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #4CAF50;")
        explanation_layout.addWidget(explanation_title)
        
        explanation_text = QLabel(
            "Track your business performance over time with this monthly revenue and profit analysis. "
            "The chart shows financial trends to help you identify growth patterns and seasonal variations. "
            "Use the date filter above to focus on specific time periods."
        )
        explanation_text.setWordWrap(True)
        explanation_text.setStyleSheet("font-size: 11px; color: #666; margin-bottom: 5px;")
        explanation_layout.addWidget(explanation_text)
        
        layout.addWidget(explanation_frame)
        
        # Chart section - full width
        chart_frame = QFrame()
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(16, 16, 16, 16)
        
        chart_title = QLabel("Monthly Revenue & Profits")
        chart_title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        chart_layout.addWidget(chart_title)
        
        # Create matplotlib figure and canvas
        self.performance_figure = Figure(figsize=(14, 8), dpi=100)
        self.performance_canvas = FigureCanvas(self.performance_figure)

        # Set initial theme for matplotlib based on current theme
        self._set_chart_theme()

        chart_layout.addWidget(self.performance_canvas)
        
        layout.addWidget(chart_frame)
        
        return tab
    
    def get_performance_months(self) -> int:
        """Get the selected number of months for performance chart."""
        text = self.performance_date_range.currentText()
        mapping = {
            "3 Months": 3,
            "6 Months": 6,
            "12 Months": 12,
            "24 Months": 24,
            "All Data": 100  # Large number to get all available data
        }
        return mapping.get(text, 12)
    
    def _update_sales_report(self, report: SalesReport) -> None:
        """Update sales tab with generated report data."""
        # Update summary labels
        self.sales_revenue_label.setText(f"₪{report.total_revenue:,.2f}")
        self.sales_transactions_label.setText(f"{report.total_transactions:,}")
        self.sales_avg_value_label.setText(f"₪{report.average_transaction_value:,.2f}")
        
        # Update table with all products (not just top products)
        self.sales_table.setRowCount(len(report.products))
        for row, product in enumerate(report.products):
            self.sales_table.setItem(row, 0, QTableWidgetItem(product["product"]))
            self.sales_table.setItem(row, 1, QTableWidgetItem(f"₪{product['revenue']:,.2f}"))
        
        # Enable export button after successful data load
        self.export_btn.setEnabled(True)
    
    def _update_inventory_report(self, report: InventoryReport) -> None:
        """Update inventory tab with generated report data."""
        # Update summary labels
        self.inventory_total_products_label.setText(f"{report.total_products:,}")
        self.inventory_total_value_label.setText(f"₪{report.total_value:,.2f}")
        
        # Update table with category breakdown
        self.inventory_table.setRowCount(len(report.category_breakdown))
        for row, (category, data) in enumerate(report.category_breakdown.items()):
            self.inventory_table.setItem(row, 0, QTableWidgetItem(category))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(f"{data['items']}"))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(f"₪{data['total_value']:,.2f}"))
        
        # Enable export button after successful data load
        self.export_btn.setEnabled(True)
    
    def _update_performance_metrics(self, metrics: PerformanceMetrics) -> None:
        """Update performance tab with generated metrics data."""
        # Only update the performance chart (table removed)
        self._update_performance_chart_with_data()
        
        # Enable export button after successful data load
        self.export_btn.setEnabled(True)

    def _update_performance_chart_with_data(self, chart_data: list = None):
        """Update the performance chart with provided data."""
        try:
            # Clear previous plot
            self.performance_figure.clear()
            
            # Get current theme colors
            theme_colors = self._get_chart_theme_colors()
            
            # Create single subplot for revenue chart
            ax = self.performance_figure.add_subplot(1, 1, 1)
            
            # Use provided data or show empty chart
            if chart_data:
                months = [data["month_name"] for data in chart_data]
                revenue_data = [data["revenue"] for data in chart_data]
            else:
                months = []
                revenue_data = []
            
            # Create chart only if there's data
            if months and revenue_data:
                # Create a beautiful revenue line chart with gradient fill
                ax.plot(months, revenue_data, color=theme_colors['line'], linewidth=3, marker='o', markersize=6, 
                       markerfacecolor=theme_colors['marker_face'], markeredgecolor=theme_colors['line'], markeredgewidth=2)
                
                # Add gradient fill under the line
                ax.fill_between(months, revenue_data, color=theme_colors['line'], alpha=0.2)
            else:
                # Show message when no data available
                ax.text(0.5, 0.5, 'No Data Available\nClick "Generate Metrics" to load data', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, color=theme_colors['text'], fontsize=12)
            
            # Styling
            ax.set_title('Monthly Revenue & Profits', color=theme_colors['text'], fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Month', color=theme_colors['text'], fontsize=12)
            ax.set_ylabel('Revenue (K₪)', color=theme_colors['text'], fontsize=12)
            ax.set_facecolor(theme_colors['background'])
            ax.tick_params(colors=theme_colors['tick'], labelsize=10)
            ax.grid(True, alpha=0.3, color=theme_colors['grid'], linestyle='--')
            
            if months and revenue_data:
                ax.tick_params(axis='x', rotation=45)
                
                for i, (month, value) in enumerate(zip(months, revenue_data)):
                    if i % 3 == 0:
                        ax.annotate(f'₪{value:.1f}K', (month, value), 
                                  textcoords="offset points", xytext=(0,10), ha='center',
                                  color=theme_colors['text'], fontsize=9, alpha=0.8)
                
                y_min = min(revenue_data) * 0.9
                y_max = max(revenue_data) * 1.1
                ax.set_ylim(y_min, y_max)
            
            self.performance_figure.tight_layout(pad=3.0)
            self.performance_figure.patch.set_facecolor(theme_colors['figure_bg'])
            self.performance_canvas.draw()
            
        except Exception as e:
            print(f"Error updating performance chart: {e}")
            # Fallback: create a simple text placeholder
            self.performance_figure.clear()
            theme_colors = self._get_chart_theme_colors()
            ax = self.performance_figure.add_subplot(1, 1, 1)
            ax.text(0.5, 0.5, 'Revenue Chart\n(Chart generation error)', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, color=theme_colors['text'], fontsize=12)
            ax.set_facecolor(theme_colors['background'])
            self.performance_figure.patch.set_facecolor(theme_colors['figure_bg'])
            self.performance_canvas.draw()

    #def _update_performance_chart(self):
    #    """Update the performance chart (empty by default, data provided by presenter)."""
    #    self._update_performance_chart_with_data()
#
    def _get_chart_theme_colors(self):
        """Get color scheme based on current theme."""
        if ThemeManager and ThemeManager.instance().theme == "light":
            return {
                'background': '#FFFFFF',
                'figure_bg': '#FFFFFF',
                'text': '#1A1A1A',
                'tick': '#666666',
                'grid': '#CCCCCC',
                'line': '#0EA5E9',
                'marker_face': '#FFFFFF'
            }
        else:
            return {
                'background': '#23272E',
                'figure_bg': '#1E1E1E',
                'text': '#EAEAEA',
                'tick': '#B0B0B0',
                'grid': '#444444',
                'line': '#00E0FF',
                'marker_face': '#FFFFFF'
            }

    def _set_chart_theme(self):
        """Set matplotlib theme based on current theme."""
        if ThemeManager and ThemeManager.instance().theme == "light":
            plt.style.use('default')  # Use default matplotlib style for light theme
        else:
            plt.style.use('dark_background')  # Use dark background for dark theme

    def _on_theme_changed(self, theme):
        """Handle theme change events."""
        self._set_chart_theme()
        self._update_performance_chart_with_data()
    
    # ---------- Notifications ----------
    def notify(self, text: str, title: str = "Info", *, critical: bool = False):
        """Show notification like pricing view."""
        if critical:
            return QMessageBox.critical(self, title, text)
        return QMessageBox.information(self, title, text)
    
    def _update_loading_status(self, is_loading: bool) -> None:
        """Update loading indicator based on operation status."""
        self.progress_bar.setVisible(is_loading)
        if is_loading:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
    

    
    def _show_error(self, error_message: str) -> None:
        """Display error messages to user in modal dialog."""
        QMessageBox.critical(self, "Error", error_message)
    
    def show_export_dialog(self) -> tuple:
        """
        Show export file dialog and return selected file path and format.
        Returns tuple (file_path, format_type) or (None, None) if cancelled.
        """
        from PySide6.QtWidgets import QFileDialog
        import os
        
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Report",
            "",
            "PDF Files (*.pdf);;JSON Files (*.json)"
        )
        
        if not file_path:
            return None, None
            
        # Determine format from file extension or selected filter
        root, ext = os.path.splitext(file_path)
        if not ext:
            if "PDF" in (selected_filter or ""):
                file_path = root + ".pdf"
                format_type = "pdf"
            elif "JSON" in (selected_filter or ""):
                file_path = root + ".json"
                format_type = "json"
            else:
                file_path = root + ".pdf"
                format_type = "pdf"
        else:
            format_type = "pdf" if file_path.lower().endswith(".pdf") else "json"
            
        return file_path, format_type
    
    def get_current_report_data(self) -> dict:
        """
        Get the currently displayed report data from the active tab.
        Returns dictionary with report type and data for export.
        """
        current_tab_index = self.tab_widget.currentIndex()
        
        if current_tab_index == 0:  # Sales tab
            return {
                "type": "sales",
                "title": "Sales Performance Report",
                "data": {
                    "Total Revenue": self.sales_revenue_label.text(),
                    "Product Count": self.sales_transactions_label.text(),
                    "Average per Product": self.sales_avg_value_label.text(),
                    "Top Products": self._get_table_data(self.sales_table)
                }
            }
        elif current_tab_index == 1:  # Inventory tab
            return {
                "type": "inventory", 
                "title": "Inventory Analysis Report",
                "data": {
                    "Total Products": self.inventory_total_products_label.text(),
                    "Total Value": self.inventory_total_value_label.text(),
                    "Category Breakdown": self._get_table_data(self.inventory_table)
                }
            }
        else:  # Performance tab (index 2)
            return {
                "type": "performance",
                "title": "Performance Metrics Report", 
                "data": {
                    "Chart Data": "Performance chart with monthly revenue trends",
                    "Note": "Performance metrics visualization available in application"
                }
            }
    
    def _get_table_data(self, table) -> list:
        """Extract data from a QTableWidget for export."""
        data = []
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data