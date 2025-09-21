import hashlib, random, sys
from typing import List, Dict, Any
from PySide6.QtWidgets import QMessageBox, QMenu, QApplication
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
        self.v.status.currentIndexChanged.connect(self.apply_filters)
        self.v.table.cellDoubleClicked.connect(self._on_dbl)
        self.v.table.customContextMenuRequested.connect(self._open_menu)

        self.reload()

    # Data
    def reload(self):
        try:
            js = self.api.list_products(include_deleted=True)
            self._data_raw = [ReadProduct.from_json(x) for x in js]
            self.apply_filters()
        except Exception as e:
            QMessageBox.critical(self.v, "Load Failed", f"{e}")

    def apply_filters(self):
        f = self.v.current_filters()
        query, f_cat, f_status = (f.get("query") or "").lower(), f.get("category"), f.get("status")

        rows: List[Dict[str, Any]] = []
        for p in self._data_raw:
            # חיפוש בסיסי לפי query
            if query and (query not in p.product_id.lower() and query not in p.name.lower()):
                continue

            rows.append({
                "ProductId": p.product_id,
                "Name": p.name,
                "Price": p.price,
                "Quantity": p.quantity,
                "IsDeleted": p.is_deleted,
                "UpdatedAt": getattr(p, "updated_at", None)
            })

        self.v.set_rows(rows)

    # Detail
    def _on_dbl(self, r: int, _c: int):
        item = self.v.table.item(r, 0)  # עמודה 0 = ProductId
        pid = item.text() if item else ""
        if pid:
            self.on_open(pid)


    def on_open(self, product_id: str):
        try:
            js = self.api.get_product(product_id)
            panel = DetailPanel(self.v, is_new=False, product=js, sales_series=sales_series_for(product_id))
            panel.save_requested.connect(self.detail_save)
            panel.delete_requested.connect(self.on_delete)
            panel.cancel_requested.connect(self.v.show_placeholder)
            self.v.set_detail_widget(panel)
        except Exception as e:
            QMessageBox.critical(self.v, "Open Failed", f"{e}")

    def on_add(self):
        panel = DetailPanel(self.v, is_new=True, product=None, sales_series=[])
        panel.save_requested.connect(self.detail_save)
        panel.delete_requested.connect(self.on_delete)
        panel.cancel_requested.connect(self.v.show_placeholder)
        self.v.set_detail_widget(panel)

    def detail_save(self, vals: dict, is_new: bool):
        try:
            if is_new:
                self.api.create_product(vals["product_id"], vals["name"], float(vals["price"]), int(vals["quantity"]))
            else:
                self.api.update_product(vals["product_id"], name=vals["name"], price=float(vals["price"]), quantity=int(vals["quantity"]))
            self.reload()
            pid = vals["product_id"]
            panel = DetailPanel(self.v, is_new=False, product=vals, sales_series=sales_series_for(pid))
            panel.save_requested.connect(self.detail_save)
            panel.delete_requested.connect(self.on_delete)
            panel.cancel_requested.connect(self.v.show_placeholder)
            self.v.set_detail_widget(panel)
        except Exception as e:
            QMessageBox.critical(self.v, "Save Failed", f"{e}")

    def on_delete(self, product_id: str):
        if not product_id:
            QMessageBox.information(self.v, "Select", "Select a row first.")
            return
        try:
            self.api.delete_product(product_id)
            self.reload()
            self.v.show_placeholder()
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


