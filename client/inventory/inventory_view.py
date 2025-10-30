from __future__ import annotations
from typing import List, Dict, Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QComboBox,
    QSplitter, QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox, QFrame,
    QFormLayout, QDoubleSpinBox, QCheckBox, QMessageBox, QStackedLayout, QMenu, QApplication
)
from PySide6.QtGui import QPixmap

import cloudinary, cloudinary.uploader, requests
import os
from dotenv import load_dotenv
load_dotenv()
import re
import tempfile

api_base = os.getenv("URL", "http://localhost:8000")

class side_panel(QFrame):
    # moreDetailsRequested = Signal(str)  # <-- נורה עם product_id כשלוחצים על הכפתור

    def __init__(self):
        super().__init__()

        top = QVBoxLayout(self)
        top.setContentsMargins(12, 12, 12, 12)
        top.setSpacing(8)

        # header
        self.title = QLabel("Details")
        top.addWidget(self.title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)

        self.id = QLineEdit("")
        self.name = QLineEdit("")
        self.price = QDoubleSpinBox(); self.price.setRange(0, 1_000_000); self.price.setDecimals(2)
        self.qty = QSpinBox(); self.qty.setRange(0, 1_000_000)
        self.brand = QLineEdit("")
        self.category = QLineEdit("")
        self.is_promo = QCheckBox("On Promotion")

        self.id.setReadOnly(True)
        self.name.setReadOnly(True)
        self.brand.setReadOnly(True)
        self.category.setReadOnly(True)
        self.price.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.qty.setButtonSymbols(QSpinBox.NoButtons)
        self.price.setEnabled(False)
        self.qty.setEnabled(False)
        self.is_promo.setEnabled(False)

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

        btns = QHBoxLayout()
        self.btn_cancel = QPushButton("Close")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        btns.addStretch(1)
        self.btn_more = QPushButton("More details →")
        self.btn_more.setCursor(Qt.PointingHandCursor)
        btns.addWidget(self.btn_cancel)
        btns.addWidget(self.btn_more)

        self.image_url = None  
        self.image = QLabel()
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setFixedSize(260, 260)
        self.image.setStyleSheet("border: 2px dashed gray; border-radius: 8px; color: #888;")
        self.image.setText("➕\nUpload Image")

        self.btn_upload = QPushButton("📤 Upload / Replace Image")
        self.btn_upload.setCursor(Qt.PointingHandCursor)
        self.btn_upload.clicked.connect(self._upload_image)

        top.addWidget(self.image)
        top.addWidget(self.btn_upload)


        top.addStretch(1)
        top.addLayout(btns)

    def set_form_data(self, data: Dict[str, Any],):
        pid = data.get("product_id", "") or ""
        self.title.setText(f"Details: {pid}" if pid else "Details")
        self.id.setText(pid)
        self.name.setText(data.get("name", "") or "")
        self.price.setValue(float(data.get("price", 0.0) or 0.0))
        self.qty.setValue(int(data.get("quantity", 0) or 0))
        self.brand.setText(data.get("brand", "") or "")
        self.category.setText(data.get("category", "") or "")
        self.is_promo.setChecked(bool(data.get("is_on_promotion", 0)))

        self.image_url = data.get("image_url") or None
        self._show_image()
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
# need to make this code as MVP

#########################################################################################
    import os, requests, cloudinary, cloudinary.uploader
    from PySide6.QtGui import QPixmap
    from PySide6.QtCore import Qt
        
    cloudinary.config(
        cloud_name=os.getenv("cloudinaryCloudName", "your_cloud_name"),
        api_key=os.getenv("cloudinaryApiKey", "your_api_key"),
        api_secret=os.getenv("cloudinaryApiSecret", "your_api_secret")
    )

    
    def _save_image_url_to_server(self, product_id: str, image_url: str) -> None:
        try:
            requests.post(
                f"{api_base}/command/product/{product_id}/UploadImage",
                json={"image_url": image_url},
                timeout=10
            )
        except Exception:
            pass

    def _force_transformed_cloudinary_url(url: str, transform: str = "f_png,q_auto") -> str:
        # הופך .../upload/... ל- .../upload/f_png,q_auto/...
        # עובד על secure_url רגיל מקלאודינרי
        return re.sub(r"/upload(/|$)", rf"/upload/{transform}\1", url, count=1)

    def _show_image(self):
        url = (self.image_url or "").strip()
        if not url:
            self.image.setPixmap(QPixmap())
            self.image.setText("➕\nUpload Image")
            return

        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (Qt)"} )

        def _try(url_try: str) -> bool:
            try:
                r = session.get(url_try, timeout=10)
                if not r.ok:
                    print("IMG HTTP ERR:", r.status_code, url_try)
                    return False

                pm = QPixmap()
                if not pm.loadFromData(r.content):
                    # שמור לקובץ זמני כדי לבדוק מה קיבלנו (ולראות אם Qt מצליח מהדיסק)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
                        f.write(r.content)
                        tmp = f.name
                    ok2 = pm.load(tmp)
                    print("QPixmap from data failed; from file:", ok2, "ctype:", r.headers.get("content-type"), "len:", len(r.content), "path:", tmp)
                    if not ok2:
                        try:
                            os.remove(tmp)
                        except Exception:
                            pass
                        return False
                    try:
                        os.remove(tmp)
                    except Exception:
                        pass
                self.image.setPixmap(pm.scaled(260, 260, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.image.setText("")
                return True
            except Exception as e:
                print("IMG EXC:", repr(e), url_try)
                return False

        # ניסיון רגיל
        if _try(url):
            return

        # אם זה Cloudinary – נכפה PNG (וגם אפשר לשנות גודל בצד ה-CDN)
        if "res.cloudinary.com" in url:
            url2 = self._force_transformed_cloudinary_url(url, "f_png,q_auto,w_260,h_260,c_fit")
            if _try(url2):
                # אם הצליח – אפשר אפילו לעדכן את self.image_url להשתמש בגרסת ה-PNG
                self.image_url = url2
                return

        # נכשל – החזר ברירת מחדל
        self.image.setPixmap(QPixmap())
        self.image.setText("➕\nUpload Image")
   
    def _upload_image(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Select Image")
        if not path:
            return

        up = cloudinary.uploader.upload(
            path,
            resource_type="image",
            folder="products",
            unique_filename=True,
            overwrite=True
        )
        self.image_url = up["secure_url"]   

        pid = (self.id.text() or "").strip()
        if pid and self.image_url:
            self._save_image_url_to_server(pid, self.image_url)

        self._show_image()
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################

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
        self.search = QLineEdit(placeholderText="Search name or product ID…")
        self.search.setFixedHeight(32)
      

        self.category = QComboBox()
        self.category.addItem("All")
        self.category.setFixedHeight(32)
        self.category.setFixedWidth(100)
       
        self.brand = QComboBox()
        self.brand.addItem("All")
        self.brand.setFixedHeight(32)
        self.brand.setFixedWidth(100)

        self.refresh = QPushButton("Refresh")
        self.refresh.setFixedHeight(32)
        self.refresh.setCursor(Qt.PointingHandCursor)

        bar.addWidget(self.title)
        bar.addSpacing(8)
        bar.addWidget(self.search, 2)
        bar.addWidget(self.category)
        bar.addWidget(self.brand)
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
        
        # Add tooltips to table headers
        header_tooltips = [
            "Product name as shown to customers",
            "Unique product identifier",
            "Current selling price per unit",
            "Available stock quantity",
            "Whether product is currently on promotional discount"
        ]
        
        for i, tooltip in enumerate(header_tooltips):
            self.table.horizontalHeaderItem(i).setToolTip(tooltip)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setToolTip("Double-click to view details")

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.table.setSortingEnabled(True)
        header.setSortIndicatorShown(True)

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

    # open detail panel
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

    # close detail panel
    def collapse_detail(self):
        if self._detail_widget is not None:
            self.stack.removeWidget(self._detail_widget)
            self._detail_widget.deleteLater()
            self._detail_widget = None
        self.detail_host.hide()
        self.split.setSizes([1, 0])

    # notifications
    def notify(self, text: str, title: str = "Info", *, critical: bool = False):
        if critical:
            return QMessageBox.critical(self, title, text)
        return QMessageBox.information(self, title, text)

    # setting category options
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

    # setting brand options
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

    