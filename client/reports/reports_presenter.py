from __future__ import annotations
from typing import Optional
import os
from .reports_model import ReportsModel
from .reports_view import ReportsView
from thread_manager import run_in_worker


class ReportsPresenter:
    """
    Presenter layer for reports module following pricing model pattern.
    """

    def __init__(self, view: ReportsView, model: ReportsModel) -> None:
        """Initialize presenter with view and model, following pricing pattern."""
        self.v = view
        self.m = model
        
        # Wire UI events like pricing presenter
        self.v.refresh_btn.clicked.connect(self.reload_all)
        self.v.export_btn.clicked.connect(self.on_export_clicked)
        self.v.sales_generate_btn.clicked.connect(self.on_generate_sales_report)
        self.v.inventory_generate_btn.clicked.connect(self.on_generate_inventory_report)
        self.v.performance_generate_btn.clicked.connect(self.on_generate_performance_metrics)
        
        # Initial load
        self.reload_all()

    # ---------- Loads ----------
    def reload_all(self) -> None:
        """Reload all reports data from API like pricing reload_all."""
        # Load all three report types
        self.on_generate_sales_report()
        self.on_generate_inventory_report() 
        self.on_generate_performance_metrics()

    # ---------- Actions ----------
    def on_generate_sales_report(self) -> None:
        """Generate sales report using API data."""
        @run_in_worker
        def load():
            return self.m.generate_sales_report()

        def on_result(sales_report):
            self.v._update_sales_report(sales_report)

        load(on_result=on_result, on_error=self._show_error)

    def on_generate_inventory_report(self) -> None:
        """Generate inventory report using API data."""
        @run_in_worker
        def load():
            return self.m.generate_inventory_report()

        def on_result(inventory_report):
            self.v._update_inventory_report(inventory_report)

        load(on_result=on_result, on_error=self._show_error)

    def on_generate_performance_metrics(self) -> None:
        """Generate performance metrics using API data."""
        # Get selected months from UI
        months = self.v.get_performance_months()
        
        @run_in_worker
        def load():
            # Get both performance metrics and chart data with selected months
            performance_metrics = self.m.generate_performance_metrics()
            chart_data = self.m.get_monthly_revenue_data(months)
            return performance_metrics, chart_data

        def on_result(result):
            performance_metrics, chart_data = result
            self.v._update_performance_metrics(performance_metrics)
            # Update chart with real data
            self.v._update_performance_chart_with_data(chart_data)

        load(on_result=on_result, on_error=self._show_error)



    def on_export_clicked(self) -> None:
        """Handle export button click - coordinates between view and model."""
        try:
            # Use view to show file dialog (view responsibility)
            file_path, format_type = self.v.show_export_dialog()
            
            if not file_path:
                return  # User cancelled
            
            # Get current report data from view (view knows what's displayed)
            report_data = self.v.get_current_report_data()
            
            # If it's a performance report, enhance with chart data
            if report_data.get("type") == "performance":
                months = self.v.get_performance_months()
                chart_data = self.m.get_monthly_revenue_data(months)
                # Add chart data to the report
                report_data["data"]["Monthly Revenue Data"] = chart_data
                report_data["data"]["Chart Description"] = f"Monthly revenue trends for the last {months} months"
            
            # Use model to perform the export (model responsibility)
            @run_in_worker
            def export():
                if format_type.lower() == "pdf":
                    self.m.export_to_pdf(report_data, file_path)
                elif format_type.lower() == "json":
                    self.m.export_to_json(report_data, file_path)
                else:
                    raise ValueError(f"Unsupported export format: {format_type}")
                return file_path
            
            def on_result(exported_path):
                self.v.notify(f"Report exported successfully to {os.path.basename(exported_path)}")
            
            export(on_result=on_result, on_error=self._show_error)
            
        except Exception as e:
            self._show_error(e)

    # ---------- Utilities ----------
    def _show_error(self, e: Exception) -> None:
        """Show error message like pricing presenter."""
        self.v.notify(f"Operation Failed: {e}", "Error", critical=True)


# Factory like pricing presenter
def create_reports_page(base_url: Optional[str] = None) -> ReportsView:
    """Create reports page with presenter following pricing pattern."""
    view = ReportsView()
    model = ReportsModel(base_url=base_url)
    view.presenter = ReportsPresenter(view, model)
    return view