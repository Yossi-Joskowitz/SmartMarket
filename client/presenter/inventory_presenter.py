import hashlib, random, sys
from typing import List, Dict, Any
from PySide6.QtWidgets import QMessageBox, QMenu, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from view.inventory_view import InventoryView, DetailPanel
from model.inventory_model import ApiService, ReadProduct



def sales_series_for(pid: str, points: int=12) -> List[int]:
    h = int(hashlib.sha256(pid.encode("utf-8")).hexdigest(), 16) % (10**8)
    rng = random.Random(h)
    base = rng.randint(30, 160)
    series, val = [], base
    for _ in range(points):
        val = max(0, val + rng.randint(-20, 20))
        series.append(val)
    return series


# Presenter
class InventoryPresenter:
    def __init__(self, view: InventoryView, api: ApiService):
        self.v = view
        self.api = api
        self._data_raw: List[ReadProduct] = []

        # Wire all signals
        self.v.refresh.clicked.connect(self.reload)
        self.v.add_btn.clicked.connect(self.on_add)
        self.v.search.textChanged.connect(self.apply_filters)
        self.v.category.currentIndexChanged.connect(self.apply_filters)
        self.v.brand.currentTextChanged.connect(self.apply_filters)  
        self.v.table.cellDoubleClicked.connect(self._on_dbl)
        self.v.table.customContextMenuRequested.connect(self._open_menu)

        self.reload()

    # Data
    def reload(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            # ברירת מחדל: לא להביא מחוקים
            js = self.api.list_products(include_deleted=False)
            self._data_raw = [ReadProduct.from_json(x) for x in js]

            # ערכים ייחודיים, ממוין אלפביתית, ללא ריקים
            categories = sorted({(p.category or "").strip() for p in self._data_raw if (p.category or "").strip()})
            brands     = sorted({(p.brand or "").strip() for p in self._data_raw if (p.brand or "").strip()})

            self.v.set_category_options(categories)
            self.v.set_brand_options(brands)

            self.apply_filters()
        except Exception as e:
            QMessageBox.critical(self.v, "Load Failed", f"{e}")
        finally:
            QApplication.restoreOverrideCursor()

    def apply_filters(self):
        f = self.v.current_filters()
        query = (f.get("query") or "").lower()
        f_category = f.get("category")
        f_brand = f.get("brand")

        try:
            js = self.api.list_products(include_deleted=False)
            self._data_raw = [ReadProduct.from_json(x) for x in js]
        except Exception as e:
            QMessageBox.critical(self.v, "Load Failed", f"{e}")
            return

        rows: List[Dict[str, Any]] = []
        for p in self._data_raw:
            # חיפוש חופשי
            if query and (query not in (p.product_id or "").lower() and query not in (p.name or "").lower()):
                continue

            # סינון לפי קטגוריה (אם נבחרה)
            if f_category and p.category != f_category:
                continue

            # סינון לפי חברה (אם נבחרה)
            if f_brand and p.brand != f_brand:
                continue

            rows.append({
                "Name": p.name or "",
                "ProductId": p.product_id or "",
                "Price": float(p.price) if p.price is not None else None,
                "Quantity": int(p.quantity) if p.quantity is not None else None,
                "IsOnPromotion": getattr(p, "is_on_promotion", False),
            })

        self.v.set_rows(rows)

        # עדכון אופציות לקטגוריות/חברות באופן דינמי
        cats = sorted(set(p.category for p in self._data_raw if p.category))
        brs = sorted(set(p.brand for p in self._data_raw if p.brand))
        self.v.set_category_options(cats)
        self.v.set_brand_options(brs)


    # Detail
    def _on_dbl(self, r: int, _c: int):
        item = self.v.table.item(r, 1)  # 1 = ProductId
        pid = item.text() if item else ""
        if pid:
            self.on_open(pid)



    def on_open(self, product_id: str):
        try:
            js = self.api.get_product(product_id)  # מחזיר snake_case
            product_payload = {
                "product_id": js.get("product_id", ""),
                "name": js.get("name", ""),
                "price": js.get("price", 0.0),
                "quantity": js.get("quantity", 0),
                "brand": js.get("brand"),
                "category": js.get("category"),
                "is_on_promotion": 1 if js.get("is_on_promotion") else 0,
                "updated_at": js.get("updated_at"),
            }
            panel = DetailPanel(self.v, is_new=False, product=product_payload,
                                sales_series=sales_series_for(product_id))
            panel.save_requested.connect(self.detail_save)
            panel.delete_requested.connect(self.on_delete)
            panel.cancel_requested.connect(self._on_close_detail)
            self.v.show_detail_widget(panel)
        except Exception as e:
            QMessageBox.critical(self.v, "Open Failed", f"{e}")

    def on_add(self):
        panel = DetailPanel(self.v, is_new=True, product=None, sales_series=[])
        panel.save_requested.connect(self.detail_save)
        panel.delete_requested.connect(self.on_delete)
        panel.cancel_requested.connect(self._on_close_detail)
        self.v.show_detail_widget(panel)

    def detail_save(self, vals: dict, is_new: bool):
        try:
            pid = vals["product_id"]
            name = vals["name"]
            price = float(vals["price"])
            qty = int(vals["quantity"])
            brand = vals.get("brand") or None
            category = vals.get("category") or None
            is_promo = 1 if vals.get("is_on_promotion") else 0  # שמור כ-int

            if is_new:
                self.api.create_product(
                    pid, name, price, qty,
                    brand=brand, category=category, is_on_promotion=is_promo
                )
            else:
                self.api.update_product(
                    pid,
                    name=name, price=price, quantity=qty,
                    brand=brand, category=category, is_on_promotion=is_promo
                )

            self.reload()
            self.v.notify("Product '{}' {}.".format(pid, "created" if is_new else "updated"))
            self.v.collapse_detail()
        except Exception as e:
            QMessageBox.critical(self.v, "Save Failed", f"{e}")

    def _on_close_detail(self):
        self.v.collapse_detail()


    def on_delete(self, product_id: str):
        if not product_id:
            QMessageBox.information(self.v, "Select", "Select a row first.")
            return
        try:
            self.api.delete_product(product_id)
            self.reload()
            self.v.notify(f"Product '{product_id}' deleted.")
            self.v.collapse_detail()
        except Exception as e:
            QMessageBox.critical(self.v, "Delete Failed", f"{e}")

    # Context menu
    def _open_menu(self, pos):
        menu = QMenu(self.v)
        a_add = QAction("Add Product", self.v); a_add.triggered.connect(self.on_add)
        pid = self.v.selected_product_id()
        a_edit = QAction("Edit Product", self.v); a_edit.triggered.connect(lambda: self.on_open(pid))
        a_del = QAction("Delete Product", self.v); a_del.triggered.connect(lambda: self.on_delete(pid))
        menu.addAction(a_add)
        if pid:
            menu.addAction(a_edit); menu.addAction(a_del)
        menu.exec(self.v.table.viewport().mapToGlobal(pos))


def create_inventory_page(parent=None, api: ApiService | None = None):
    view = InventoryView(parent)
    api = api or ApiService()
    view.presenter = InventoryPresenter(view, api)  
    return view


