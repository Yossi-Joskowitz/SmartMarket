from __future__ import annotations
from typing import List, Dict, Any


from view.inventory_view import InventoryView, DetailPanel
from model.inventory_model import InventoryModel, ReadProduct



class InventoryPresenter:
    def __init__(self, view: InventoryView, model: InventoryModel):
        self.v = view
        self.m = model
        self._data_raw: List[ReadProduct] = []
        self._all_categories: List[str] = []
        self._all_brands: List[str] = []

        # Wire all UI events
        self.v.refresh.clicked.connect(self.reload)
        self.v.add_btn.clicked.connect(self.on_add)
        self.v.search.textChanged.connect(self.apply_filters)
        self.v.category.currentIndexChanged.connect(self.apply_filters)
        self.v.brand.currentTextChanged.connect(self.apply_filters)
        self.v.table.cellDoubleClicked.connect(self._on_dbl)
        self.v.table.customContextMenuRequested.connect(self._open_menu)

        self._load_filter_options()
        self.reload()

    def reload(self,):
        self.v.cursor_wait()
        try:
            self._load_filter_options()
            self.apply_filters()
        finally:
            self.v.cursor_wait(False)

    def _load_filter_options(self):
        try:
            cats = self.m.distinct_categories()
            brs  = self.m.distinct_brands()
            self._all_categories = sorted({(c or "").strip() for c in cats if (c or "").strip()})
            self._all_brands     = sorted({(b or "").strip() for b in brs  if (b or "").strip()})
            # מעדכן את ה־View; הוא כבר יודע לשמר בחירה אם אפשר וליפול ל-"All" אם לא
            self.v.set_category_options(self._all_categories)
            self.v.set_brand_options(self._all_brands)
        except Exception as e:
            self.v.notify(f"Failed to load filter options: {e}", "Error", critical=True)
    
    def apply_filters(self):
        f = self.v.current_filters()
        try:
            js = self.m.list_products(
                include_deleted=False,
                query=f.get("query") or None,
                category=f.get("category") or None,
                brand=f.get("brand") or None,
            )
            self._data_raw = [ReadProduct.from_json(x) for x in js]
        except Exception as e:
            self.v.notify(f"Failed to load products: {e}", "Error", critical=True)
            return

        rows = [{
            "Name": p.name or "",
            "ProductId": p.product_id or "",
            "Price": float(p.price) if p.price is not None else None,
            "Quantity": int(p.quantity) if p.quantity is not None else None,
            "IsOnPromotion": bool(getattr(p, "is_on_promotion", False)),
        } for p in self._data_raw]

        self.v.set_rows(rows)


    # ---------- Detail ----------
    def _on_dbl(self, r: int, _c: int):
        item = self.v.table.item(r, 1)  # 1 = ProductId
        pid = item.text() if item else ""
        if pid:
            self.on_open(pid)

    def on_open(self, product_id: str):
        try:
            js = self.m.get_product(product_id)
            payload = {
                "product_id": js.get("product_id", ""),
                "name": js.get("name", ""),
                "price": js.get("price", 0.0),
                "quantity": js.get("quantity", 0),
                "brand": js.get("brand"),
                "category": js.get("category"),
                "is_on_promotion": 1 if js.get("is_on_promotion") else 0,
            }
            panel = DetailPanel(self.v, is_new=False)
            panel.set_form_data(payload, is_new=False)

            # חיבורים לכפתורים
            panel.btn_save.clicked.connect(lambda checked=False, p=panel: self.detail_save(p))
            panel.btn_cancel.clicked.connect(self._on_close_detail)
            # הוספת Delete רק לעריכה
            panel.btn_delete = self.v.create_btn("Delete", "background:#23272E;color:#F44336;border:1px solid #F44336;border-radius:8px;padding:0 14px;font-weight:700;")
            panel.layout().itemAt(panel.layout().count() - 1).layout().insertWidget(1, panel.btn_delete)  # להכניס בין Close ל-Save
            panel.btn_delete.clicked.connect(lambda checked=False, p=panel: self.on_delete(p.get_product_id()))

            self.v.show_detail_widget(panel)
        except Exception as e:
            self.v.notify(f"Open Failed: {e}", "Error", critical=True)

    def on_add(self):
        panel = DetailPanel(self.v, is_new=True)
        panel.set_form_data({
            "product_id": "",
            "name": "",
            "price": 0.0,
            "quantity": 0,
            "brand": "",
            "category": "",
            "is_on_promotion": 0,
        }, is_new=True)

        panel.btn_save.clicked.connect(lambda checked=False, p=panel: self.detail_save(p))
        panel.btn_cancel.clicked.connect(self._on_close_detail)
        # אין Delete בפריט חדש

        self.v.show_detail_widget(panel)

    def detail_save(self, panel: DetailPanel):
        try:
            vals = panel.get_form_data()
            is_new = panel.is_new

            # ולידציה בסיסית
            if not vals["product_id"]:
                return panel.show_error("Product ID is required.")
            if not vals["name"]:
                return panel.show_error("Name is required.")
            if float(vals["price"]) < 0 or int(vals["quantity"]) < 0:
                return panel.show_error("Price/Quantity cannot be negative.")

            pid = vals["product_id"]
            if is_new:
                self.m.create_product(
                    pid, vals["name"], float(vals["price"]), int(vals["quantity"]),
                    brand=(vals.get("brand") or None),
                    category=(vals.get("category") or None),
                    is_on_promotion=1 if vals.get("is_on_promotion") else 0
                )
            else:
                self.m.update_product(
                    pid,
                    name=vals["name"],
                    price=float(vals["price"]),
                    quantity=int(vals["quantity"]),
                    brand=(vals.get("brand") or None),
                    category=(vals.get("category") or None),
                    is_on_promotion=1 if vals.get("is_on_promotion") else 0
                )

            self.reload()
            self.v.notify(f"Product '{pid}' {'created' if is_new else 'updated'}.")
            self.v.collapse_detail()
        except Exception as e:
            self.v.notify(f"Save Failed: {e}", "Error", critical=True)

    def _on_close_detail(self):
        self.v.collapse_detail()

    def on_delete(self, product_id: str):
        if not product_id:
            self.v.notify("Select a row first.", "Select")
            return
        try:
            self.m.delete_product(product_id)
            self.reload()
            self.v.notify(f"Product '{product_id}' deleted.")
            self.v.collapse_detail()
        except Exception as e:
            self.v.notify(f"Delete Failed: {e}", "Error", critical=True)

    # ---------- Context menu ----------
    def _open_menu(self, pos):
        action, pid = self.v.open_context_menu(pos)
        if action == "add":
            self.on_add()
        elif action == "edit" and pid:
            self.on_open(pid)
        elif action == "delete" and pid:
            self.on_delete(pid)



def create_inventory_page() -> InventoryView:
    view = InventoryView()
    model = InventoryModel()
    view.presenter = InventoryPresenter(view, model)
    return view
