from typing import List, Dict, Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QComboBox,
    QSplitter, QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox, QFrame,
    QFormLayout, QDoubleSpinBox, QCheckBox, QMessageBox ,QStackedLayout
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
    # signals: שמירת טופס / מחיקה / סגירה
    save_requested = Signal(dict, bool)   # (values, is_new)
    delete_requested = Signal(str)        # product_id
    cancel_requested = Signal()

    def __init__(self, parent=None, *, is_new: bool=False,
                 product: Optional[Dict[str, Any]]=None,
                 sales_series: Optional[list]=None):
        super().__init__(parent)
        self.setStyleSheet(
            "QFrame{background:#23272E;border:1px solid #2B2B2B;border-radius:10px}"
        )
        self.is_new = is_new
        self._product = product or {
            "product_id": "",
            "name": "",
            "price": 0.0,
            "quantity": 0,
            "brand": "",
            "category": "",
            "is_on_promotion": 0,
        }

        top = QVBoxLayout(self)
        top.setContentsMargins(12, 12, 12, 12)
        top.setSpacing(8)

        # כותרת
        title = QLabel("New Product" if is_new else f"Edit: {self._product.get('product_id','')}")
        title.setStyleSheet("color:#B0B0B0;font-weight:600;")
        top.addWidget(title)

        # טופס
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)

        self.id = QLineEdit(self._product.get("product_id", ""))
        self.id.setReadOnly(not is_new)  # לא מאפשרים לשנות מזהה בפריט קיים

        self.name = QLineEdit(self._product.get("name", ""))

        self.price = QDoubleSpinBox()
        self.price.setRange(0, 1_000_000)
        self.price.setDecimals(2)
        self.price.setValue(self._safe_float(self._product.get("price"), 0.0))

        self.qty = QSpinBox()
        self.qty.setRange(0, 1_000_000)
        self.qty.setValue(self._safe_int(self._product.get("quantity"), 0))

        # שדות נוספים (רק להצגה/עריכה – לא חובה להשתמש בהם כרגע)
        self.brand = QLineEdit(self._product.get("brand", "") or "")
        self.category = QLineEdit(self._product.get("category", "") or "")
        self.is_promo = QCheckBox("On Promotion")
        self.is_promo.setChecked(bool(self._product.get("is_on_promotion", 0)))

        # גובה אחיד
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
        top.addLayout(form)

        # גרף מכירות קטן (אם קיים Sparkline)
        if Sparkline is not None:
            chart_title = QLabel("Recent Sales")
            chart_title.setStyleSheet("color:#B0B0B0;")
            self.chart = Sparkline(self)
            self.chart.setMinimumHeight(160)
            try:
                self.chart.set_series(sales_series or [])
            except Exception:
                pass
            top.addWidget(chart_title)
            top.addWidget(self.chart)

        # כפתורים
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
        btns.addWidget(self.btn_cancel)
        btns.addWidget(self.btn_save)

        if not is_new:
            self.btn_delete = QPushButton("Delete")
            self.btn_delete.setStyleSheet(
                "background:#23272E;color:#F44336;border:1px solid #F44336;"
                "border-radius:8px;padding:0 14px;font-weight:700;"
            )
            btns.insertWidget(1, self.btn_delete)

        top.addLayout(btns)

        # חיבורים
        self.btn_save.clicked.connect(self._emit_save)
        self.btn_cancel.clicked.connect(self.cancel_requested.emit)
        if not is_new:
            self.btn_delete.clicked.connect(
                lambda: self.delete_requested.emit(self.id.text().strip())
            )

    # שמירה – בניית payload בטוח
    def _emit_save(self):
        vals = {
            "product_id": self.id.text().strip(),
            "name": self.name.text().strip(),
            "price": self._safe_float(self.price.value(), 0.0),
            "quantity": self._safe_int(self.qty.value(), 0),
            "brand": self.brand.text().strip(),
            "category": self.category.text().strip(),
            "is_on_promotion": 1 if self.is_promo.isChecked() else 0,
        }

        # ולידציה בסיסית
        if not vals["product_id"] or not vals["name"]:
            QMessageBox.warning(self, "Validation", "Product ID and Name are required.")
            return

        self.save_requested.emit(vals, self.is_new)

    # עזרים בטוחים למספרים
    @staticmethod
    def _safe_float(v, default=0.0) -> float:
        try:
            if v is None or v == "":
                return default
            return float(v)
        except Exception:
            return default

    @staticmethod
    def _safe_int(v, default=0) -> int:
        try:
            if v is None or v == "":
                return default
            return int(v)
        except Exception:
            return default



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
        self.category.addItem("All")
        self.category.setFixedHeight(32)
        self.category.setStyleSheet("background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;border-radius:8px;padding:0 8px;")

        self.brand = QComboBox()
        self.brand.setEditable(True)
        self.brand.lineEdit().setPlaceholderText("Brand…")
        self.brand.addItem("All")
        self.brand.setFixedHeight(32)
        self.brand.setStyleSheet("background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;border-radius:8px;padding:0 8px;")
        
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
        bar.addWidget(self.brand)
        bar.addWidget(self.refresh)
        bar.addWidget(self.add_btn)
        bar.addStretch(1)
        vbox.addLayout(bar)

        # Splitter
        self.split = QSplitter(Qt.Horizontal)
        self.split.setHandleWidth(1)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Name", "ProductId", "Price", "Quantity", "Promotion"
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
        self.stack = QStackedLayout(self.detail_host)
        self.stack.setContentsMargins(12,12,12,12)

        self.placeholder = QLabel("Double-click a product to view & edit.\nOr click 'Add' to create a new one.")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("color:#6C7480;")

        self.stack.addWidget(self.placeholder)   # index 0
        self._detail_widget = None

        self.split.addWidget(self.detail_host)

        
        self.detail_host.hide()
        self.split.setSizes([1, 0])
        vbox.addWidget(self.split, 1)

    # API
    def set_rows(self, rows):
        was_sorting = self.table.isSortingEnabled()
        if was_sorting: self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        for r in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Name (טקסט)
            self.table.setItem(row, 0, QTableWidgetItem(str(r.get("Name",""))))
            # ProductId (SKU)
            self.table.setItem(row, 1, QTableWidgetItem(str(r.get("ProductId",""))))
            # Price (מספר)
            price_item = QTableWidgetItem()
            price = r.get("Price")
            if price is not None:
                price_item.setData(Qt.DisplayRole, float(price))
                price_item.setData(Qt.EditRole, float(price))
            self.table.setItem(row, 2, price_item)
            # Quantity (מספר)
            qty_item = QTableWidgetItem()
            qty = r.get("Quantity")
            if qty is not None:
                qty_item.setData(Qt.DisplayRole, int(qty))
                qty_item.setData(Qt.EditRole, int(qty))
            self.table.setItem(row, 3, qty_item)
            # Promotion (Yes/No)
            promo_txt = "Yes" if r.get("IsOnPromotion") else "No"
            self.table.setItem(row, 4, QTableWidgetItem(promo_txt))

        if was_sorting:
            self.table.setSortingEnabled(True)


    def current_filters(self) -> Dict[str, Any]:
        cat = self.category.currentText()
        br  = self.brand.currentText()
        return {
            "query": self.search.text().strip(),
            "category": None if cat == "All" else cat,
            "brand": None if br == "All" or not br.strip() else br.strip(),
        }

    def selected_product_id(self) -> str:
        sel = self.table.selectionModel().selectedRows() if self.table.selectionModel() else []
        if not sel: return ""
        r = sel[0].row()
        item = self.table.item(r, 1)  # עמודה 1 = ProductId
        return item.text() if item else ""

    def show_detail_widget(self, widget: QWidget):
        if self._detail_widget is not None:
            self.stack.removeWidget(self._detail_widget)
            self._detail_widget.deleteLater()
            self._detail_widget = None
        self._detail_widget = widget
        self.stack.addWidget(widget)
        self.detail_host.show()
        # יחסי רוחב נעימים (התאם כרצונך)
        self.split.setSizes([760, 380])
        self.stack.setCurrentWidget(widget)

    def collapse_detail(self):
        # סגירת חלון צד והחזרת הטבלה לרוחב מלא
        if self._detail_widget is not None:
            self.stack.removeWidget(self._detail_widget)
            self._detail_widget.deleteLater()
            self._detail_widget = None
        self.detail_host.hide()
        self.split.setSizes([1, 0])

    def notify(self, text: str, title: str = "Info"):
        QMessageBox.information(self, title, text)

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
        # אם המשתמש הקליד מותג שלא ברשימה – נשמר את הטקסט שהקליד
        if current and current not in (["All"] + brands):
            self.brand.setEditText(current)
        self.brand.blockSignals(False)


