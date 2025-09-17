from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QComboBox,
    QSplitter, QTableWidget, QTableWidgetItem, QHeaderView, QToolButton, QSpinBox, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
import random


class Sparkline(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.series = []

    def set_series(self, data):
        self.series = data or []
        self.update()

    def paintEvent(self, _):
        if not self.series:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(self.rect(), QColor("#23272E"))
        pen = QPen(QColor("#B0B0B0"), 2)
        p.setPen(pen)
        # normalize to widget
        mn, mx = min(self.series), max(self.series)
        span = (mx - mn) or 1
        pts = []
        for i, v in enumerate(self.series):
            x = int(i * (w - 12) / max(1, len(self.series) - 1)) + 6
            y = h - 8 - int((v - mn) * (h - 16) / span)
            pts.append((x, y))
        # grid (light)
        p.setPen(QPen(QColor("#2B2B2B"), 1))
        for gy in (h//4, h//2, 3*h//4):
            p.drawLine(6, gy, w-6, gy)
        # line
        p.setPen(QPen(QColor("#00E0FF"), 3))
        for i in range(1, len(pts)):
            p.drawLine(pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1])


def create_inventory_view(data_service=None):
    """
    Compact Inventory page (PySide6-only).
    - Optional data_service.get_products(query, page, page_size, sort_by, sort_dir, filters)
    """
    # root & layout
    root = QWidget()
    vbox = QVBoxLayout(root); vbox.setContentsMargins(16,16,16,16); vbox.setSpacing(10)

    # --- toolbar ---
    bar = QHBoxLayout()
    title = QLabel("📦 Inventory"); title.setStyleSheet("color:#00E0FF;font-weight:700;")
    search = QLineEdit(placeholderText="Search product / SKU…")
    for w in (search,):
        w.setFixedHeight(32); w.setStyleSheet("background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;border-radius:8px;padding:0 10px;")
    category = QComboBox(); category.addItems(["All", "Beverages","Dairy","Bakery","Produce"])
    status = QComboBox(); status.addItems(["All","OK","Low","Critical","Overstock"])
    for w in (category, status):
        w.setFixedHeight(32); w.setStyleSheet("background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;border-radius:8px;padding:0 8px;")
    refresh = QPushButton("Refresh"); export = QPushButton("Export CSV")
    for b in (refresh, export):
        b.setFixedHeight(32); b.setCursor(Qt.PointingHandCursor)
    refresh.setStyleSheet("background:#00E0FF;color:#23272E;border:none;border-radius:8px;padding:0 12px;font-weight:600;")
    export.setStyleSheet("background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;border-radius:8px;padding:0 12px;")
    bar.addWidget(title); bar.addSpacing(8); bar.addWidget(search,2); bar.addWidget(category); bar.addWidget(status); bar.addWidget(refresh); bar.addWidget(export); bar.addStretch(1)
    vbox.addLayout(bar)

    # --- splitter: table | right panel ---
    split = QSplitter(Qt.Horizontal); split.setHandleWidth(1)

    table = QTableWidget(0, 8)
    table.setHorizontalHeaderLabels(["Product","SKU","Stock","InTransit","Forecast","Status","Vendor","Lead/ MOQ"])
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QTableWidget.SingleSelection)
    header = table.horizontalHeader(); header.setStretchLastSection(True); header.setSectionResizeMode(QHeaderView.Stretch)
    table.setStyleSheet(
        "QTableWidget{background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;border-radius:10px}"
        "QHeaderView::section{background:#23272E;color:#00E0FF;border:none;font-weight:600}"
        "QTableWidget::item:selected{background:#00E0FF33;color:#00E0FF}"
    )
    split.addWidget(table)

    right = QFrame(); right.setStyleSheet("QFrame{background:#23272E;border:1px solid #2B2B2B;border-radius:10px}")
    rv = QVBoxLayout(right); rv.setContentsMargins(12,12,12,12); rv.setSpacing(8)
    rtitle = QLabel("Stock vs Forecast"); rtitle.setStyleSheet("color:#B0B0B0;font-weight:600;")
    chart = Sparkline(); chart.setMinimumHeight(160)
    btns = QHBoxLayout(); approve = QPushButton("Approve"); reject = QPushButton("Reject")
    for b in (approve, reject): b.setFixedHeight(32); b.setCursor(Qt.PointingHandCursor)
    approve.setStyleSheet("background:#00E0FF;color:#23272E;border:none;border-radius:8px;padding:0 14px;font-weight:700;")
    reject.setStyleSheet("background:#23272E;color:#F44336;border:1px solid #F44336;border-radius:8px;padding:0 14px;font-weight:700;")
    btns.addStretch(1); btns.addWidget(approve); btns.addWidget(reject)
    rv.addWidget(rtitle); rv.addWidget(chart,1); rv.addLayout(btns)
    split.addWidget(right)
    split.setSizes([720, 380])
    vbox.addWidget(split, 1)

    # --- pager ---
    pager = QHBoxLayout()
    prevb, nextb = QToolButton(text="◀ Prev"), QToolButton(text="Next ▶")
    for b in (prevb, nextb): b.setCursor(Qt.PointingHandCursor)
    size = QSpinBox(); size.setRange(10,200); size.setValue(20); size.setStyleSheet("background:#23272E;color:#B0B0B0;border:1px solid #2B2B2B;border-radius:8px;padding:0 6px;")
    page_lbl = QLabel("Page 1"); page_lbl.setStyleSheet("color:#B0B0B0")
    pager.addWidget(prevb); pager.addWidget(nextb); pager.addSpacing(12); pager.addWidget(QLabel("Rows:")); pager.addWidget(size); pager.addStretch(1); pager.addWidget(page_lbl)
    vbox.addLayout(pager)

    # --- state + helpers ---
    state = {"page":1, "query":"", "filters":{"category":None, "status":None}}

    def status_item(txt):
        it = QTableWidgetItem(txt)
        low = txt.lower()
        it.setForeground(QColor("#4CAF50") if low in ("ok","normal") else QColor("#FFC107") if low=="low" else QColor("#F44336") if low in ("critical","stockout") else QColor("#B0B0B0"))
        return it

    def plot_for_sku(sku):
        xs = [random.randint(40, 200) for _ in range(12)]
        fs = [v + random.randint(-20, 20) for v in xs]
        chart.set_series(xs)  # you can swap to fs as needed; minimal sparkline

    def load_page():
        table.setRowCount(0)
        try:
            rows = []
            if data_service:
                rows = data_service.get_products(
                    query=state["query"], page=state["page"], page_size=size.value(),
                    sort_by="sku", sort_dir="asc", filters=state["filters"]
                ) or []
            else:
                raise RuntimeError("mock")
        except Exception:
            rows = [
                {"Product":"Whole Milk 1L","SKU":"SKU-100","Stock":124,"InTransit":40,"Forecast":135,"Status":"OK","Vendor":"DairyCo","Lead":"3d","MOQ":24},
                {"Product":"Sourdough Bread","SKU":"SKU-101","Stock":22,"InTransit":10,"Forecast":60,"Status":"Low","Vendor":"BakeIt","Lead":"2d","MOQ":12},
                {"Product":"Tomatoes 1kg","SKU":"SKU-102","Stock":8,"InTransit":25,"Forecast":50,"Status":"Critical","Vendor":"AgriFresh","Lead":"1d","MOQ":10},
                {"Product":"Olive Oil 750ml","SKU":"SKU-103","Stock":210,"InTransit":0,"Forecast":160,"Status":"Overstock","Vendor":"Olivia","Lead":"5d","MOQ":6},
            ]
        for r in rows:
            row = table.rowCount(); table.insertRow(row)
            table.setItem(row,0,QTableWidgetItem(str(r.get("Product",""))))
            table.setItem(row,1,QTableWidgetItem(str(r.get("SKU",""))))
            table.setItem(row,2,QTableWidgetItem(str(r.get("Stock",""))))
            table.setItem(row,3,QTableWidgetItem(str(r.get("InTransit",""))))
            table.setItem(row,4,QTableWidgetItem(str(r.get("Forecast",""))))
            table.setItem(row,5,status_item(str(r.get("Status",""))))
            table.setItem(row,6,QTableWidgetItem(str(r.get("Vendor",""))))
            table.setItem(row,7,QTableWidgetItem(f"{r.get('Lead','')} / {r.get('MOQ','')}"))
        page_lbl.setText(f"Page {state['page']}")
        if table.rowCount(): plot_for_sku(table.item(0,1).text())

    # --- wiring ---
    def apply_and_reload(): state["page"]=1; load_page()
    search.textChanged.connect(lambda: (state.update({"query":search.text().strip()}), apply_and_reload()))
    category.currentIndexChanged.connect(lambda _:(state["filters"].update({"category":None if category.currentText()=="All" else category.currentText()}), apply_and_reload()))
    status.currentIndexChanged.connect(lambda _:(state["filters"].update({"status":None if status.currentText()=="All" else status.currentText()}), apply_and_reload()))
    prevb.clicked.connect(lambda: (state.update({"page":max(1, state["page"]-1)}), load_page()))
    nextb.clicked.connect(lambda: (state.update({"page":state["page"]+1}), load_page()))
    size.valueChanged.connect(lambda _:(state.update({"page":1}), load_page()))
    table.cellDoubleClicked.connect(lambda r, _c: plot_for_sku(table.item(r,1).text()))
    refresh.clicked.connect(load_page)
    export.clicked.connect(lambda: print_csv(table))  # minimal export to stdout

    # auto-refresh
    t = QTimer(root); t.setInterval(15000); t.timeout.connect(load_page); t.start()

    load_page()
    return root


def print_csv(table: QTableWidget):
    import csv, sys
    w = csv.writer(sys.stdout)
    w.writerow([table.horizontalHeaderItem(i).text() for i in range(table.columnCount())])
    for r in range(table.rowCount()):
        w.writerow([table.item(r, c).text() if table.item(r, c) else "" for c in range(table.columnCount())])
