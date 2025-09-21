from typing import List, Dict, Any
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QComboBox,
    QSplitter, QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox, QFrame,
    QFormLayout, QDoubleSpinBox
)


class Sparkline(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.series = []

    def set_series(self, data):
        self.series = data or []
        self.update()

    def paintEvent(self, _):
        if not self.series:
            p = QPainter(self)
            p.fillRect(self.rect(), QColor("#23272E"))
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(self.rect(), QColor("#23272E"))
        mn, mx = min(self.series), max(self.series)
        span = (mx - mn) or 1
        pts = []
        for i, v in enumerate(self.series):
            x = int(i * (w - 12) / max(1, len(self.series) - 1)) + 6
            y = h - 8 - int((v - mn) * (h - 16) / span)
            pts.append((x, y))
        p.setPen(QPen(QColor("#2B2B2B"), 1))
        for gy in (h//4, h//2, 3*h//4):
            p.drawLine(6, gy, w-6, gy)
        p.setPen(QPen(QColor("#00E0FF"), 3))
        for i in range(1, len(pts)):
            p.drawLine(pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1])


# -----------------------------
class DetailPanel(QFrame):
    save_requested = Signal(dict, bool)   # values, is_new
    delete_requested = Signal(str)        # product_id
    cancel_requested = Signal()

    def __init__(self, parent=None, *, is_new=False, product=None, sales_series=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame{background:#23272E;border:1px solid #2B2B2B;border-radius:10px}")
        self.is_new = is_new
        self._product = product or {"product_id":"", "name":"", "price":0.0, "quantity":0}

        top = QVBoxLayout(self); top.setContentsMargins(12,12,12,12); top.setSpacing(8)
        title = QLabel("New Product" if is_new else f"Edit: {self._product.get('product_id','')}")
        title.setStyleSheet("color:#B0B0B0;font-weight:600;")
        top.addWidget(title)

        form = QFormLayout()
        self.id = QLineEdit(self._product.get("product_id","")); self.id.setReadOnly(not is_new)
        self.name = QLineEdit(self._product.get("name",""))
        self.price = QDoubleSpinBox(); self.price.setRange(0, 1_000_000); self.price.setDecimals(2); self.price.setValue(float(self._product.get("price",0.0)))
        self.qty = QSpinBox(); self.qty.setRange(0, 1_000_000); self.qty.setValue(int(self._product.get("quantity",0)))
        for w in (self.id, self.name, self.price, self.qty):
            if hasattr(w, "setFixedHeight"): w.setFixedHeight(32)
        form.addRow("Product ID:", self.id)
        form.addRow("Name:", self.name)
        form.addRow("Price:", self.price)
        form.addRow("Quantity:", self.qty)
        top.addLayout(form)

        # Sales chart
        chart_title = QLabel("Recent Sales"); chart_title.setStyleSheet("color:#B0B0B0;")
        self.chart = Sparkline(); self.chart.setMinimumHeight(160)
        self.chart.set_series(sales_series or [])
        top.addWidget(chart_title)
        top.addWidget(self.chart)

        # Buttons
        btns = QHBoxLayout()
        self.btn_save = QPushButton("Save"); self.btn_save.setStyleSheet("background:#00E0FF;color:#23272E;border:none;border-radius:8px;padding:0 14px;font-weight:700;")
        self.btn_cancel = QPushButton("Close"); self.btn_cancel.setStyleSheet("background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;border-radius:8px;padding:0 14px;")
        btns.addStretch(1); btns.addWidget(self.btn_cancel); btns.addWidget(self.btn_save)
        if not is_new:
            self.btn_delete = QPushButton("Delete"); self.btn_delete.setStyleSheet("background:#23272E;color:#F44336;border:1px solid #F44336;border-radius:8px;padding:0 14px;font-weight:700;")
            btns.insertWidget(1, self.btn_delete)
        top.addLayout(btns)

        self.btn_save.clicked.connect(self._emit_save)
        self.btn_cancel.clicked.connect(self.cancel_requested.emit)
        if not is_new:
            self.btn_delete.clicked.connect(lambda: self.delete_requested.emit(self.id.text().strip()))

    def _emit_save(self):
        vals = {
            "product_id": self.id.text().strip(),
            "name": self.name.text().strip(),
            "price": float(self.price.value()),
            "quantity": int(self.qty.value()),
        }
        if not vals["product_id"] or not vals["name"]:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation", "Product ID and Name are required.")
            return
        self.save_requested.emit(vals, self.is_new)


# -----------------------------
class InventoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        vbox = QVBoxLayout(self); vbox.setContentsMargins(16,16,16,16); vbox.setSpacing(10)

        # Toolbar
        bar = QHBoxLayout()
        self.title = QLabel("📦 Inventory"); self.title.setStyleSheet("color:#00E0FF;font-weight:700;")
        self.search = QLineEdit(placeholderText="Search product / SKU…")
        self.search.setFixedHeight(32)
        self.search.setStyleSheet("background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;border-radius:8px;padding:0 10px;")
        
        self.category = QComboBox()
        self.category.addItems(["All","Beverages","Dairy","Bakery","Produce","Frozen","Snacks","Household","Personal Care"])
        
        self.status = QComboBox()
        self.status.addItems(["All","OK","Low","Critical","Overstock","Deleted"])
        for w in (self.category, self.status):
            w.setFixedHeight(32)
            w.setStyleSheet("background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;border-radius:8px;padding:0 8px;")
        
        self.refresh = QPushButton("Refresh"); self.add_btn = QPushButton("Add")
        for b in (self.refresh, self.add_btn):
            b.setFixedHeight(32)
            b.setCursor(Qt.PointingHandCursor)
        self.refresh.setStyleSheet("background:#00E0FF;color:#23272E;border:none;border-radius:8px;padding:0 12px;font-weight:600;")
        self.add_btn.setStyleSheet("background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;border-radius:8px;padding:0 12px;")
        
        bar.addWidget(self.title)
        bar.addSpacing(8)
        bar.addWidget(self.search,2)
        bar.addWidget(self.category)
        bar.addWidget(self.status)
        bar.addWidget(self.refresh)
        bar.addWidget(self.add_btn)
        bar.addStretch(1)
        vbox.addLayout(bar)

        # Splitter
        self.split = QSplitter(Qt.Horizontal)
        self.split.setHandleWidth(1)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ProductId", "Name", "Price", "Quantity", "IsDeleted", "UpdatedAt"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Stretch)

        # ⬅️ מיון בלחיצה על כותרת
        self.table.setSortingEnabled(True)
        header.setSortIndicatorShown(True)  # אופציונלי: מציג חץ כיוון מיון

        self.table.setStyleSheet(
            "QTableWidget{background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;border-radius:10px}"
            "QHeaderView::section{background:#23272E;color:#00E0FF;border:none;font-weight:600}"
            "QTableWidget::item:selected{background:#00E0FF33;color:#00E0FF}"
        )

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.split.addWidget(self.table)


        self.detail_host = QFrame()
        self.detail_layout = QVBoxLayout(self.detail_host)
        self.detail_layout.setContentsMargins(12,12,12,12)
        self.detail_layout.setSpacing(8)
        self.placeholder = QLabel("Double-click a product to view & edit.\nOr click 'Add' to create a new one.")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("color:#6C7480;")
        self.detail_layout.addWidget(self.placeholder)
        self.split.addWidget(self.detail_host)
        self.split.setSizes([760, 380])
        vbox.addWidget(self.split, 1)

    # API
    def set_rows(self, rows):
    # rows = רשימת מילונים ישירות מה-DB, עם מפתחות: ProductId, Name, Price, Quantity, IsDeleted, UpdatedAt

        was_sorting = self.table.isSortingEnabled()
        if was_sorting:
            self.table.setSortingEnabled(False)

        self.table.setRowCount(0)

        def _set_text(row, col, value):
            item = QTableWidgetItem()
            item.setData(Qt.DisplayRole, "" if value is None else str(value))
            self.table.setItem(row, col, item)

        def _set_number(row, col, value):
            item = QTableWidgetItem()
            try:
                num = float(value)
                item.setData(Qt.DisplayRole, num)
                item.setData(Qt.EditRole, num)  # כדי שמיון יהיה מספרי
            except Exception:
                item.setData(Qt.DisplayRole, "" if value is None else str(value))
            self.table.setItem(row, col, item)

        for r in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)

            _set_text  (row, 0, r.get("ProductId"))
            _set_text  (row, 1, r.get("Name"))
            _set_number(row, 2, r.get("Price"))
            _set_number(row, 3, r.get("Quantity"))
            _set_text  (row, 4, r.get("IsDeleted"))
            _set_text  (row, 5, r.get("UpdatedAt"))

        if was_sorting:
            self.table.setSortingEnabled(True)

    def current_filters(self) -> Dict[str, Any]:
        return {
            "query": self.search.text().strip(),
            "category": None if self.category.currentText()=="All" else self.category.currentText(),
            "status": None if self.status.currentText()=="All" else self.status.currentText(),
        }

    def selected_product_id(self) -> str:
        sel = self.table.selectionModel().selectedRows() if self.table.selectionModel() else []
        if not sel:
            return ""
        r = sel[0].row()
        item = self.table.item(r, 1)
        return item.text() if item else ""

    def set_detail_widget(self, widget: QWidget):
        while self.detail_layout.count():
            w = self.detail_layout.takeAt(0).widget()
            if w: w.deleteLater()
        self.detail_layout.addWidget(widget)

    def show_placeholder(self):
        while self.detail_layout.count():
            w = self.detail_layout.takeAt(0).widget()
            if w: w.deleteLater()
        self.detail_layout.addWidget(self.placeholder)
