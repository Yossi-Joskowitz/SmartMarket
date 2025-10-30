"""
Reports Model Layer - MVP Pattern Implementation
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import requests
import json ,os

from dotenv import load_dotenv
load_dotenv()



class ReportType(Enum):
    """Enumeration of available report types for filtering and generation."""
    SALES = "sales"
    INVENTORY = "inventory"
    PERFORMANCE = "performance"


@dataclass
class SalesReport:
    """
    Sales performance report containing revenue and transaction data.
    """
    id: str
    total_revenue: float
    total_transactions: int
    average_transaction_value: float
    products: List[Dict[str, Any]]  # Changed from top_selling_products to products to show all


@dataclass
class InventoryReport:
    """
    Inventory status report showing stock levels and movement data.
    """
    id: str
    total_products: int
    total_value: float
    category_breakdown: Dict[str, Dict[str, Any]]


@dataclass
class PerformanceMetrics:
    """
    Overall system performance metrics and KPIs.
    """
    id: str


class ReportsModel:
    """
    Model layer for reports generation using MVP pattern and real API data.
    Inspired by the pricing model structure.
    """
    
    def __init__(self, base_url: Optional[str] = None, timeout: float = 15.0) -> None:
        """Initialize reports model with API configuration."""
        self.base_url = base_url or os.getenv("URL", "http://localhost:8000")
        self.session = requests.Session()
        self.timeout = timeout
    
    def get_products_profit(self) -> List[Dict[str, Any]]:
        """Fetch products profit data from API."""
        url = f"{self.base_url}/query/products_profit"
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
    
    def get_products_category_value(self) -> List[Dict[str, Any]]:
        """Fetch products category value data from API."""
        url = f"{self.base_url}/query/products_category_value"
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
    
    def get_products_total_profit_per_month(self) -> List[Dict[str, Any]]:
        """Fetch products total profit per month data from API."""
        url = f"{self.base_url}/query/products_total_profit_per_month"
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
    
    def generate_sales_report(self) -> SalesReport:
        """Generate comprehensive sales performance report using real API data."""
        try:
            # Fetch data from APIs
            products_data = self.get_products_profit()
            
            # Calculate total revenue from products (only positive profits for sales)
            total_revenue = sum(product.get("total_profit", 0) for product in products_data if product.get("total_profit", 0) > 0)
            
            # Count products with positive profit
            product_count = len([p for p in products_data if p.get("total_profit", 0) > 0])
            
            # Calculate average revenue per product
            avg_revenue_per_product = total_revenue / product_count if product_count > 0 else 0.0
            
            # Process products for display (sorted by profit)
            products_list = []
            sorted_products = sorted(products_data, key=lambda x: x.get("total_profit", 0), reverse=True)
            for product in sorted_products:
                revenue = product.get("total_profit", 0)
                if revenue > 0:
                    # Try multiple possible field names for the product name
                    product_name = (
                        product.get("name") or 
                        product.get("product_name") or 
                        product.get("product_id", f"Product {len(products_list) + 1}")
                    )
                    products_list.append({
                        "product": product_name,
                        "revenue": revenue
                    })
            
            # Generate current timestamp for report
            now = datetime.now()
            
            return SalesReport(
                id=f"SALES_{now.strftime('%Y%m%d_%H%M%S')}",
                total_revenue=total_revenue,
                total_transactions=product_count,
                average_transaction_value=avg_revenue_per_product,
                products=products_list
            )
            
        except requests.RequestException as e:
            print(f"API Error generating sales report: {e}")
            return self._create_empty_sales_report()
        except Exception as e:
            print(f"Error generating sales report: {e}")
            return self._create_empty_sales_report()
    
    def generate_inventory_report(self) -> InventoryReport:
        """
        Generate current inventory status and analysis report using real API data.
        """
        try:
            # Fetch real data from API
            category_data = self.get_products_category_value()
            
            # Calculate inventory metrics from real data
            total_products = sum(item.get("total_quantity", 0) for item in category_data)
            total_value = sum(item.get("total_inventory_value", 0) for item in category_data)
            
            # Category breakdown from real API data only (simplified without turnover)
            category_breakdown = {}
            for item in category_data:
                category = item.get("category", "Unknown")
                category_breakdown[category] = {
                    "items": item.get("total_quantity", 0),
                    "total_value": item.get("total_inventory_value", 0)
                }
            
            return InventoryReport(
                id=f"INV_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                total_products=total_products,
                total_value=total_value,
                category_breakdown=category_breakdown
            )
            
        except requests.RequestException as e:
            print(f"API Error generating inventory report: {e}")
            return self._create_empty_inventory_report()
        except Exception as e:
            print(f"Error generating inventory report: {e}")
            return self._create_empty_inventory_report()

    def generate_performance_metrics(self) -> PerformanceMetrics:
        """
        Generate overall system performance metrics and KPIs using real API data.
        """
        try:
            return PerformanceMetrics(
                id=f"PERF_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
        except requests.RequestException as e:
            print(f"API Error generating performance metrics: {e}")
            return self._create_empty_performance_metrics()
        except Exception as e:
            print(f"Error generating performance metrics: {e}")
            return self._create_empty_performance_metrics()
    
    def get_monthly_revenue_data(self, months: int = 12) -> List[Dict[str, Any]]:
        """
        Get monthly revenue data for chart visualization.
        """
        try:
            monthly_data = self.get_products_total_profit_per_month()
            
            # Sort by year and month, take the most recent entries
            sorted_data = sorted(monthly_data, 
                               key=lambda x: (x.get("year", 2024), x.get("month", 1)))
            recent_data = sorted_data[-months:] if len(sorted_data) >= months else sorted_data
            
            # Convert to chart format with month names
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            chart_data = []
            for record in recent_data:
                month_num = record.get("month", 1)
                month_name = month_names[month_num - 1] if 1 <= month_num <= 12 else f"M{month_num}"
                profit = record.get("total_profit", 0)
                
                chart_data.append({
                    "month_name": month_name,
                    "month_num": month_num,
                    "year": record.get("year", 2024),
                    "revenue": profit / 1000.0  # Convert to thousands for display
                })
            
            return chart_data
            
        except requests.RequestException as e:
            print(f"API Error getting monthly revenue data: {e}")
            return []
        except Exception as e:
            print(f"Error getting monthly revenue data: {e}")
            return []
    
    def _create_empty_inventory_report(self) -> InventoryReport:
        """Create empty inventory report when API fails."""
        return InventoryReport(
            id=f"INV_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            total_products=0,
            total_value=0.0,
            category_breakdown={}
        )
    
    def _create_empty_performance_metrics(self) -> PerformanceMetrics:
        """Create empty performance metrics when API fails."""
        return PerformanceMetrics(
            id=f"PERF_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

    def _create_empty_sales_report(self) -> SalesReport:
        """Create empty sales report when API fails."""
        now = datetime.now()
        return SalesReport(
            id=f"SALES_{now.strftime('%Y%m%d_%H%M%S')}",
            total_revenue=0.0,
            total_transactions=0,
            average_transaction_value=0.0,
            products=[]
        )
    
    def export_to_json(self, report_data: dict, file_path: str) -> None:
        """
        Export report data to clean, readable JSON format.
        
        Args:
            report_data: Dictionary containing report information and data
            file_path: Full path where the JSON file should be saved
        """
        # Ensure target directory exists
        parent_dir = os.path.dirname(file_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        
        # Create simple, clean JSON structure
        title = report_data.get("title", "SmartMarket Report")
        report_type = report_data.get("type", "unknown")
        data = report_data.get("data", {})
        
        # Clean format - convert table data to readable structure
        clean_data = {}
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], list):
                    # Convert table data to list of objects
                    if "Products" in key:
                        clean_data[key] = [{"name": row[0], "value": row[1]} for row in value if len(row) >= 2]
                    elif "Category" in key:
                        clean_data[key] = [{"category": row[0], "items": row[1], "value": row[2]} for row in value if len(row) >= 3]
                    else:
                        clean_data[key] = value
                elif isinstance(value[0], dict) and "month_name" in value[0]:
                    # Handle monthly revenue data (chart data)
                    clean_data[key] = [
                        {
                            "month": item.get("month_name", "Unknown"),
                            "year": item.get("year", 2024),
                            "revenue_thousands": item.get("revenue", 0)
                        } 
                        for item in value
                    ]
                else:
                    clean_data[key] = value
            else:
                clean_data[key] = str(value)
        
        # Final export structure
        export_data = {
            "title": title,
            "type": report_type,
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": clean_data
        }
        
        # Write to JSON file with clean formatting
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=4, ensure_ascii=False)
    
    def export_to_pdf(self, report_data: dict, file_path: str) -> None:
        """
        Export report data to actual PDF format - simple and readable.
        
        Args:
            report_data: Dictionary containing report information and data  
            file_path: Full path where the PDF file should be saved
        """
        # Ensure target directory exists
        parent_dir = os.path.dirname(file_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        
        try:
            # Try matplotlib for simple PDF generation (most likely to be available)
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_pdf import PdfPages
            import matplotlib.patches as patches
            
            title = report_data.get("title", "SmartMarket Report")
            report_type = report_data.get("type", "unknown")
            data = report_data.get("data", {})
            
            with PdfPages(file_path) as pdf:
                # Create first page
                fig, ax = plt.subplots(figsize=(8.5, 11), facecolor='white')  # Standard letter size with white background
                fig.patch.set_facecolor('white')  # Ensure white background
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                ax.set_facecolor('white')  # Set axes background to white
                
                # Title
                ax.text(0.5, 0.95, title.upper(), fontsize=16, weight='bold', 
                       ha='center', va='top', color='black')
                
                # Report info
                ax.text(0.5, 0.88, f"Report Type: {report_type.title()}", 
                       fontsize=12, ha='center', va='top', color='black')
                ax.text(0.5, 0.84, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                       fontsize=10, ha='center', va='top', color='black')
                
                # Draw separator line
                ax.plot([0.1, 0.9], [0.80, 0.80], 'k-', linewidth=1)
                
                # Add content
                y_pos = 0.75
                for key, value in data.items():
                    if y_pos < 0.1:  # New page needed
                        pdf.savefig(fig, bbox_inches='tight', facecolor='white')
                        plt.close(fig)
                        fig, ax = plt.subplots(figsize=(8.5, 11), facecolor='white')
                        fig.patch.set_facecolor('white')  # Ensure white background
                        ax.set_xlim(0, 1)
                        ax.set_ylim(0, 1)
                        ax.axis('off')
                        ax.set_facecolor('white')  # Set axes background to white
                        y_pos = 0.95
                    
                    # Section header
                    ax.text(0.05, y_pos, f"{key}:", fontsize=12, weight='bold', 
                           ha='left', va='top', color='black')
                    y_pos -= 0.04
                    
                    # Section content
                    if isinstance(value, list) and len(value) > 0:
                        if isinstance(value[0], list):
                            # Table data
                            for row in value[:10]:  # Limit to 10 rows per section
                                if y_pos < 0.1:
                                    break
                                row_text = " | ".join(str(cell) for cell in row)
                                ax.text(0.1, y_pos, row_text, fontsize=9, 
                                       ha='left', va='top', family='monospace', color='black')
                                y_pos -= 0.025
                        elif isinstance(value[0], dict) and "month_name" in value[0]:
                            # Handle monthly revenue data (chart data)
                            for item in value[:12]:  # Limit to 12 months
                                if y_pos < 0.1:
                                    break
                                month = item.get("month_name", "Unknown")
                                year = item.get("year", 2024)
                                revenue = item.get("revenue", 0)
                                ax.text(0.1, y_pos, f"{month} {year}: ₪{revenue:.1f}K", fontsize=9,
                                       ha='left', va='top', family='monospace', color='black')
                                y_pos -= 0.025
                        else:
                            # Simple list
                            for item in value[:10]:  # Limit to 10 items
                                if y_pos < 0.1:
                                    break
                                ax.text(0.1, y_pos, f"• {str(item)}", fontsize=9, 
                                       ha='left', va='top', color='black')
                                y_pos -= 0.025
                    else:
                        # Simple value
                        ax.text(0.1, y_pos, str(value), fontsize=10, 
                               ha='left', va='top', color='black')
                        y_pos -= 0.03
                    
                    y_pos -= 0.02  # Extra space between sections
                
                # Add footer
                ax.text(0.5, 0.05, "Generated by SmartMarket Analytics", 
                       fontsize=8, ha='center', va='bottom', style='italic', color='black')
                
                # Save the page
                pdf.savefig(fig, bbox_inches='tight', facecolor='white')
                plt.close(fig)
                
        except ImportError:
            # Fallback: Create simple text file with .pdf extension
            self._create_text_pdf_fallback(report_data, file_path)
    
    def _create_text_pdf_fallback(self, report_data: dict, file_path: str) -> None:
        """Create a simple text-based file when matplotlib is not available."""
        title = report_data.get("title", "SmartMarket Report")
        report_type = report_data.get("type", "unknown")
        data = report_data.get("data", {})
        
        content = []
        content.append(title.upper())
        content.append("=" * len(title))
        content.append("")
        content.append(f"Report Type: {report_type.title()}")
        content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        content.append("-" * 60)
        content.append("")
        
        for key, value in data.items():
            content.append(f"{key.upper()}:")
            content.append("-" * len(key))
            
            if isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], list):
                    # Table format
                    for row in value:
                        content.append("  " + " | ".join(str(cell) for cell in row))
                elif isinstance(value[0], dict) and "month_name" in value[0]:
                    # Handle monthly revenue data (chart data)
                    for item in value:
                        month = item.get("month_name", "Unknown")
                        year = item.get("year", 2024)
                        revenue = item.get("revenue", 0)
                        content.append(f"  {month} {year}: ₪{revenue:.1f}K")
                else:
                    # List format
                    for item in value:
                        content.append(f"  • {str(item)}")
            else:
                content.append(f"  {str(value)}")
            
            content.append("")
        
        content.append("-" * 60)
        content.append("Generated by SmartMarket Analytics System")
        
        # Write as text file (readable in any text editor)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))