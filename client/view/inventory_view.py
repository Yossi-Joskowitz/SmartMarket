from __future__ import annotations
from typing import List, Dict, Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QComboBox,
    QSplitter, QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox, QFrame,
    QFormLayout, QDoubleSpinBox, QCheckBox, QMessageBox, QStackedLayout, QMenu, QApplication
)


class DetailPanel(QFrame):
    def __init__(self, parent: Optional[QWidget] = None, *, is_new: bool = False):
        super().__init__(parent)
        self.is_new = is_new

        self.setStyleSheet(
            "QFrame{background:#23272E;border:1px solid #2B2B2B;border-radius:10px}"
        )

        top = QVBoxLayout(self)
        top.setContentsMargins(12, 12, 12, 12)
        top.setSpacing(8)

        # header
        self.title = QLabel("New Product" if is_new else "Edit")
        self.title.setStyleSheet("color:#B0B0B0;font-weight:600;")
        top.addWidget(self.title)

        
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)

        self.id = QLineEdit("")
        self.id.setReadOnly(not is_new)  
        
        self.name = QLineEdit("")

        self.price = QDoubleSpinBox()
        self.price.setRange(0, 1_000_000)
        self.price.setDecimals(2)

        self.qty = QSpinBox()
        self.qty.setRange(0, 1_000_000)

        self.brand = QLineEdit("")
        self.category = QLineEdit("")
        self.is_promo = QCheckBox("On Promotion")

        for w in (self.id, self.name, self.price, self.qty, self.brand, self.category):
            if hasattr(w, "setFixedHeight"):
                w.setFixedHeight(32)

        form.addRow("Product ID:", self.id)
        form.addRow("Name:", self.name)
        form.addRow("Price:", self.price)
        form.addRow("Quantity:", self.qty)
        form.addRow("Brand:", self.brand)
        form.addRow("Category:", self.category)
        form.addRow("", self.is_promo)
        
        form_container = QWidget()
        form_container.setLayout(form)
        form_container.setMaximumWidth(520)  

        center_row = QHBoxLayout()
        center_row.addWidget(form_container)
        top.addLayout(center_row)

        # Buttons
        btns = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_save.setStyleSheet(
            "background:#00E0FF;color:#23272E;border:none;border-radius:8px;"
            "padding:0 14px;font-weight:700;"
        )
        self.btn_cancel = QPushButton("Close")
        self.btn_cancel.setStyleSheet(
            "background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;"
            "border-radius:8px;padding:0 14px;"
        )
        btns.addStretch(1)
        self.btn_delete: Optional[QPushButton] = None
        
        btns.addWidget(self.btn_cancel)
        btns.addWidget(self.btn_save)
        top.addStretch(1)          
        top.addLayout(btns)

    def set_form_data(self, data: Dict[str, Any], *, is_new: bool):
        self.is_new = is_new
        pid = data.get("product_id", "") or ""
        self.title.setText("New Product" if is_new else f"Edit: {pid}")
        self.id.setText(pid)
        self.id.setReadOnly(not is_new)
        self.name.setText(data.get("name", "") or "")
        self.price.setValue(float(data.get("price", 0.0) or 0.0))
        self.qty.setValue(int(data.get("quantity", 0) or 0))
        self.brand.setText(data.get("brand", "") or "")
        self.category.setText(data.get("category", "") or "")
        self.is_promo.setChecked(bool(data.get("is_on_promotion", 0)))

    def get_form_data(self) -> Dict[str, Any]:
        return {
            "product_id": self.id.text().strip(),
            "name": self.name.text().strip(),
            "price": float(self.price.value()),
            "quantity": int(self.qty.value()),
            "brand": self.brand.text().strip(),
            "category": self.category.text().strip(),
            "is_on_promotion": 1 if self.is_promo.isChecked() else 0,
        }

    def get_product_id(self) -> str:
        return self.id.text().strip()

    def show_error(self, msg: str):
        QMessageBox.warning(self, "Validation", msg)


class InventoryView(QWidget):
    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(16, 16, 16, 16)
        vbox.setSpacing(10)

        # Toolbar
        bar = QHBoxLayout()
        self.title = QLabel("📦 Inventory")
        self.title.setStyleSheet("color:#00E0FF;font-weight:700;")
        self.search = QLineEdit(placeholderText="Search name or product ID…")
        self.search.setFixedHeight(32)
        self.search.setStyleSheet(
            "background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;"
            "border-radius:8px;padding:0 10px;"
        )

        self.category = QComboBox()
        self.category.addItem("All")
        self.category.setFixedHeight(32)
        self.category.setStyleSheet(
            "background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;"
            "border-radius:8px;padding:0 8px;"
        )

        self.brand = QComboBox()
        self.brand.addItem("All")
        self.brand.setFixedHeight(32)
        self.brand.setStyleSheet(
            "background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;"
            "border-radius:8px;padding:0 8px;"
        )

        self.refresh = QPushButton("Refresh")
        self.add_btn = QPushButton("Add")
        for b in (self.refresh, self.add_btn):
            b.setFixedHeight(32)
            b.setCursor(Qt.PointingHandCursor)
        self.refresh.setStyleSheet(
            "background:#00E0FF;color:#23272E;border:none;border-radius:8px;"
            "padding:0 12px;font-weight:600;"
        )
        self.add_btn.setStyleSheet(
            "background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;"
            "border-radius:8px;padding:0 12px;"
        )

        bar.addWidget(self.title)
        bar.addSpacing(8)
        bar.addWidget(self.search, 2)
        bar.addWidget(self.category)
        bar.addWidget(self.brand)
        bar.addWidget(self.add_btn)
        bar.addWidget(self.refresh)
        bar.addStretch(1)
        vbox.addLayout(bar)

        # Splitter
        self.split = QSplitter(Qt.Horizontal)
        self.split.setHandleWidth(1)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Name", "ProductId", "Price", "Quantity", "Promotion"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.table.setSortingEnabled(True)
        header.setSortIndicatorShown(True)

        self.table.setStyleSheet(
            "QTableWidget{background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;border-radius:10px}"
            "QHeaderView::section{background:#23272E;color:#00E0FF;border:none;font-weight:600}"
            "QTableWidget::item:selected{background:#00E0FF33;color:#00E0FF}"
        )

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.split.addWidget(self.table)

        # Detail host (right)
        self.detail_host = QFrame()
        self.stack = QStackedLayout(self.detail_host)
        self.stack.setContentsMargins(12, 12, 12, 12)
        self._detail_widget: Optional[QWidget] = None

        self.split.addWidget(self.detail_host)

        self.detail_host.hide()
        self.split.setSizes([1, 0])
        vbox.addWidget(self.split, 1)

    # filling the table
    def set_rows(self, rows: List[Dict[str, Any]]):
        was_sorting = self.table.isSortingEnabled()
        if was_sorting:
            self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        for r in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(r.get("Name", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(str(r.get("ProductId", ""))))

            price_item = QTableWidgetItem()
            price = r.get("Price")
            if price is not None:
                price_item.setData(Qt.DisplayRole, float(price))
                price_item.setData(Qt.EditRole, float(price))
            self.table.setItem(row, 2, price_item)

            qty_item = QTableWidgetItem()
            qty = r.get("Quantity")
            if qty is not None:
                qty_item.setData(Qt.DisplayRole, int(qty))
                qty_item.setData(Qt.EditRole, int(qty))
            self.table.setItem(row, 3, qty_item)

            promo_txt = "Yes" if r.get("IsOnPromotion") else "No"
            self.table.setItem(row, 4, QTableWidgetItem(promo_txt))

        if was_sorting:
            self.table.setSortingEnabled(True)

    # retrieving current filters
    def current_filters(self) -> Dict[str, Any]:
        cat = self.category.currentText()
        br = self.brand.currentText()
        return {
            "query": self.search.text().strip(),
            "category": None if cat == "All" else cat,
            "brand": None if br == "All" or not br.strip() else br.strip(),
        }

    # getting selected product ID
    def selected_product_id(self) -> str:
        sm = self.table.selectionModel()
        if not sm:
            return ""
        rows = sm.selectedRows()
        if not rows:
            return ""
        item = self.table.item(rows[0].row(), 1) 
        return item.text() if item else ""


    
    def show_detail_widget(self, widget: QWidget):
        if self._detail_widget is not None:
            self.stack.removeWidget(self._detail_widget)
            self._detail_widget.deleteLater()
            self._detail_widget = None
        self._detail_widget = widget
        self.stack.addWidget(widget)
        self.detail_host.show()
        self.split.setSizes([760, 380])
        self.stack.setCurrentWidget(widget)

    def collapse_detail(self):
        if self._detail_widget is not None:
            self.stack.removeWidget(self._detail_widget)
            self._detail_widget.deleteLater()
            self._detail_widget = None
        self.detail_host.hide()
        self.split.setSizes([1, 0])

    def notify(self, text: str, title: str = "Info", *, critical: bool = False):
        if critical:
            return QMessageBox.critical(self, title, text)
        return QMessageBox.information(self, title, text)

    def set_category_options(self, categories: List[str]):
        current = self.category.currentText()
        self.category.blockSignals(True)
        self.category.clear()
        self.category.addItem("All")
        for c in categories:
            self.category.addItem(c)
        if current and current in (["All"] + categories):
            self.category.setCurrentText(current)
        self.category.blockSignals(False)

    def set_brand_options(self, brands: List[str]):
        current = self.brand.currentText()
        self.brand.blockSignals(True)
        self.brand.clear()
        self.brand.addItem("All")
        for b in brands:
            self.brand.addItem(b)
        if current and current in (["All"] + brands):
            self.brand.setCurrentText(current)
        else:
            self.brand.setCurrentIndex(0)
        self.brand.blockSignals(False)

    def cursor_wait(self, wait: bool = True):
        if wait:
            QApplication.setOverrideCursor(Qt.WaitCursor)
        else:
            QApplication.restoreOverrideCursor()

    def create_btn(self, text: str , style: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setStyleSheet(style)
        return btn
    
    def open_context_menu(self, pos):
        menu = QMenu(self)
        a_add = QPushButton("Add Product", self)

        pid = self.selected_product_id()
        a_edit = QPushButton("Edit Product", self)
        a_del  = QPushButton("Delete Product", self)

        menu.addAction(a_add)
        if pid:
            menu.addAction(a_edit)
            menu.addAction(a_del)

        chosen = menu.exec(self.table.viewport().mapToGlobal(pos))
        if chosen is None:
            return None, None
        if chosen is a_add:
            return "add", None
        if chosen is a_edit:
            return "edit", pid
        if chosen is a_del:
            return "delete", pid
        return None, None

