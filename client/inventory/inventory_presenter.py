from __future__ import annotations
from typing import List, Dict, Any
from thread_manager import run_in_worker  
from inventory.inventory_view import InventoryView, side_panel
from inventory.inventory_model import InventoryModel, ReadProduct
from pricing.pricing_presenter import create_pricing_page

class InventoryPresenter:
    def __init__(self, view: InventoryView, model: InventoryModel):
        self.v = view
        self.m = model
        self._data_raw: List[ReadProduct] = []
        self._all_categories: List[str] = []
        self._all_brands: List[str] = []

        # Wire all UI events
        self.v.refresh.clicked.connect(self.reload)
        self.v.search.textChanged.connect(self.apply_filters)
        self.v.category.currentIndexChanged.connect(self.apply_filters)
        self.v.brand.currentTextChanged.connect(self.apply_filters)
        self.v.table.cellDoubleClicked.connect(self.open_side_panel)

        self.reload()

    # ---------- Loading & Filters ----------
    def reload(self):
        """Reload table and filter options using background workers (UI-safe)."""
        self.apply_filters()
        self._load_filter_options()

    def _load_filter_options(self):
        
        @run_in_worker
        def task():
            cats = self.m.distinct_categories()
            brs = self.m.distinct_brands()
            all_categories = sorted({(c or '').strip() for c in cats if (c or '').strip()})
            all_brands = sorted({(b or '').strip() for b in brs if (b or '').strip()})
            return all_categories, all_brands

        def ok(data):
            all_categories, all_brands = data
            self._all_categories = all_categories
            self._all_brands = all_brands
            self.v.set_category_options(self._all_categories)
            self.v.set_brand_options(self._all_brands)

        def err(e: Exception):
            self.v.notify(f"Failed to load filter options: {e}", "Error", critical=True)

        task(on_result=ok, on_error=err)

    def apply_filters(self):
        """Apply current filters: fetch data in background, then update table safely."""
        # Read filters from UI (must be on UI thread)
        f: Dict[str, Any] = self.v.current_filters()
        query = f.get("query") or None
        category = f.get("category") or None
        brand = f.get("brand") or None

        @run_in_worker
        def task(q, c, b):
            js = self.m.list_products(
                query=q,
                category=c,
                brand=b,
            )
            data_raw = [ReadProduct.from_json(x) for x in js]
            rows = [{
                "Name": p.name or "",
                "ProductId": p.product_id or "",
                "Price": float(p.current_price) if p.current_price is not None else None,
                "Quantity": int(p.quantity) if p.quantity is not None else None,
                "IsOnPromotion": bool(getattr(p, "is_on_promotion", False)),
            } for p in data_raw]
            return data_raw, rows

        def ok(result):
            data_raw, rows = result
            self._data_raw = data_raw
            self.v.set_rows(rows)
            

        def err(e: Exception):
            
            self.v.notify(f"Failed to load products: {e}", "Error", critical=True)

        task(query, category, brand, on_result=ok, on_error=err)

    # ---------- Detail ----------
    def open_side_panel(self, r: int, _c: int):
        """Load product in background and build the detail panel on UI thread."""
        
        @run_in_worker
        def task(pid: str):
            js = self.m.get_product(pid)
            if not js:
                raise ValueError("Product not found")
            image_url = self.m.get_image_url(pid)
            return {
                "product_id": js.get("product_id", ""),
                "name": js.get("name", ""),
                "price": js.get("current_price", 0.0),
                "quantity": js.get("quantity", 0),
                "brand": js.get("brand"),
                "category": js.get("category"),
                "is_on_promotion": 1 if js.get("is_on_promotion") else 0,
                "image_url": image_url
            }

        def result(payload: dict):
            self.payload = payload
            panel = side_panel()
            panel.set_form_data(self.payload)
            panel.btn_more.clicked.connect(self._open_pricing)
            panel.btn_cancel.clicked.connect(self._on_close_detail)

            self.v.show_detail_widget(panel)
            

        def err(e: Exception):
            self.v.notify(f"Open Failed: {e}", "Error", critical=True)

        item = self.v.table.item(r, 1)  
        product_id = item.text() if item else ""
        if product_id:
            task(product_id, on_result=result, on_error=err)
        
    def _on_close_detail(self):
        """Pure UI."""
        self.v.collapse_detail()

    def _open_pricing(self):
        view = create_pricing_page(
            product_id=self.payload["product_id"],
            close_callback=self._on_close_detail
        )
        self.v.show_detail_widget(view)
    

def create_inventory_page() -> InventoryView:
    view = InventoryView()
    model = InventoryModel()
    view.presenter = InventoryPresenter(view, model)
    return view
