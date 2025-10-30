from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QTableWidget,
    QTableWidgetItem, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox,
    QHeaderView, QMessageBox, QFrame, QSplitter, QTextEdit
)

# Import theme manager
try:
    from ..theme_manager import ThemeManager
except ImportError:
    try:
        from theme_manager import ThemeManager
    except ImportError:
        ThemeManager = None

class PricingView(QWidget):
    
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PricingView")
        self.is_add_mode = False

        self._build_ui()
        
        # Connect to theme changes
        if ThemeManager:
            ThemeManager.instance().themeChanged.connect(self._on_theme_changed)

    # ---------- UI HELPERS (Using Theme Manager) ----------
    def _create_explanation_section(self, title: str, text: str, field_help: str = "") -> QFrame:
        """Create a standardized explanation section using theme manager styles."""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 10)
        
        title_label = QLabel(title)
        title_label.setObjectName("SectionTitle")  # Let theme manager handle styling
        layout.addWidget(title_label)
        
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setObjectName("ExplanationText")  # Let theme manager handle styling
        layout.addWidget(text_label)
        
        if field_help:
            help_label = QLabel(field_help)
            help_label.setWordWrap(True)
            help_label.setObjectName("HelpText")  # Let theme manager handle styling
            layout.addWidget(help_label)
        
        return frame

    def _create_controls_frame(self, title: str) -> QFrame:
        """Create a standardized controls frame."""
        frame = QFrame()
        frame.setFixedHeight(50)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        
        label = QLabel(title)
        layout.addWidget(label)
        layout.addStretch()
        
        return frame

    def _create_field(self, widget, tooltip: str, readonly: bool = False):
        """Create a field with tooltip."""
        widget.setToolTip(tooltip)
        if readonly and hasattr(widget, 'setReadOnly'):
            widget.setReadOnly(True)
        return widget

    def _create_money_field(self, tooltip: str) -> QDoubleSpinBox:
        """Create a money field with proper configuration."""
        spin = QDoubleSpinBox()
        spin.setRange(0, 10**9)
        spin.setDecimals(2)
        spin.setSingleStep(0.1)
        spin.setToolTip(tooltip)
        return spin

    def _create_button(self, text: str, tooltip: str) -> QPushButton:
        """Create a standardized button."""
        btn = QPushButton(text)
        btn.setFixedHeight(32)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        return btn

    def _create_form_section(self, title: str, explanation_title: str, explanation_text: str, field_help: str = "") -> tuple:
        """Create a form section with explanation and title."""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Add explanation
        explanation = self._create_explanation_section(explanation_title, explanation_text, field_help)
        layout.addWidget(explanation)
        
        # Add form title
        form_title = QLabel(title)
        form_title.setObjectName("FormTitle")  # Let theme manager handle styling
        layout.addWidget(form_title)
        
        return frame, layout

    def _on_theme_changed(self, theme: str) -> None:
        """Handle theme changes - styles are now automatically managed by theme manager."""
        pass  # Theme manager handles all styling automatically

    # ---------- UI BUILD ----------
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        # ===== Header Bar =====
        header_layout = self._create_header()
        root.addLayout(header_layout)

        # ===== Main content with tabs =====
        self.tabs = QTabWidget()
        self._create_tabs()
        root.addWidget(self.tabs, 1)

    def _create_header(self) -> QHBoxLayout:
        header_layout = QHBoxLayout()
        
        # Close button (left side)
        self.close_btn = self._create_button("← Close", "Close this view and return to previous panel")
        self.close_btn.setProperty("variant", "secondary")
        self.close_btn.hide()  # Hidden by default, shown when close callback is set
        header_layout.addWidget(self.close_btn)
        
        # Title
        self.title = QLabel("🛍️ Product Management")
        self.title.setObjectName("Title")
        header_layout.addWidget(self.title)
        
        # Product ID input section
        header_layout.addWidget(QLabel("Product ID:"))
        
        self.product_id_input = self._create_field(QLineEdit(), "Enter the unique product identifier to load product details")
        self.product_id_input.setPlaceholderText("Enter Product ID...")
        self.product_id_input.setFixedWidth(240)
        self.product_id_input.setFixedHeight(32)
        header_layout.addWidget(self.product_id_input)

        self.load_btn = self._create_button("Load Product", "Load product information from database")
        header_layout.addWidget(self.load_btn)

        header_layout.addStretch()

        # Global controls
        self.add_btn = self._create_button("Add New", "Create a new product entry")
        self.refresh_btn = self._create_button("Refresh", "Reload current product data")
        
        self.delete_btn = self._create_button("Delete", "Remove this product from database")
        self.delete_btn.setProperty("variant", "danger")

        for btn in [self.add_btn, self.refresh_btn, self.delete_btn]:
            header_layout.addWidget(btn)
        
        return header_layout

    def _create_tabs(self) -> None:
        # ===== Details Tab =====
        self.details_tab = self._create_details_tab()
        self.tabs.addTab(self.details_tab, "📋 Details & Pricing")

        # ===== Sell Tab =====
        self.sell_tab = self._create_sell_tab()
        self.tabs.addTab(self.sell_tab, "💰 Sales")

        # ===== Buy Tab =====
        self.buy_tab = self._create_buy_tab()
        self.tabs.addTab(self.buy_tab, "📦 Purchasing")

        # ===== History Tab =====
        self.history_tab = self._create_history_tab()
        self.tabs.addTab(self.history_tab, "📊 History")

        # ===== Notes Tab =====
        self.notes_tab = self._create_notes_tab()
        self.tabs.addTab(self.notes_tab, "📝 Notes & Analysis")


    def _create_details_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Controls section
        layout.addWidget(self._create_controls_frame("Product Details & Pricing"))

        # Results section with splitter
        results_splitter = QSplitter(Qt.Horizontal)

        # Product info section
        product_frame = QFrame()
        product_main_layout = QVBoxLayout(product_frame)
        product_main_layout.setContentsMargins(16, 16, 16, 16)
        product_main_layout.setSpacing(12)

        # Add explanation section
        explanation = self._create_explanation_section(
            "📦 Product Overview",
            "View and manage product information including basic details, inventory levels, and identification data. All fields are automatically populated when you load a product by ID.",
            "• Product ID: Unique identifier for this item\n• Name & Brand: Product identification details\n• Category: Product classification for organization"
        )
        product_main_layout.addWidget(explanation)

        # Product form
        form_title = QLabel("Product Information")
        form_title.setStyleSheet("font-weight: bold; margin-top: 10px;")
        product_main_layout.addWidget(form_title)

        product_layout = QFormLayout()
        product_layout.setLabelAlignment(Qt.AlignRight)

        # Create form fields with tooltips
        self.product_id = self._create_field(QLineEdit(), "Unique identifier for this product", readonly=True)
        self.name_val = self._create_field(QLineEdit(), "Product name as shown to customers", readonly=True)
        self.brand_val = self._create_field(QLineEdit(), "Brand or manufacturer of the product", readonly=True)
        self.category_val = self._create_field(QLineEdit(), "Product category for organization", readonly=True)
        self.quantity_val = self._create_field(QLineEdit(), "Current stock quantity available", readonly=True)

        for label, field in [("Product ID:", self.product_id), ("Name:", self.name_val), ("Brand:", self.brand_val), ("Category:", self.category_val), ("Quantity:", self.quantity_val)]:
            product_layout.addRow(label, field)

        product_main_layout.addLayout(product_layout)
        product_main_layout.addStretch()

        product_frame.setMinimumWidth(350)
        product_frame.setMaximumWidth(450)
        results_splitter.addWidget(product_frame)

        # Pricing section
        pricing_frame = QFrame()
        pricing_main_layout = QVBoxLayout(pricing_frame)
        pricing_main_layout.setContentsMargins(16, 16, 16, 16)
        pricing_main_layout.setSpacing(12)

        # Add pricing explanation
        pricing_explanation = self._create_explanation_section(
            "💰 Pricing Management",
            "Configure product pricing including cost and selling prices. Set up promotional discounts and manage profit margins for optimal business performance.",
            "• Cost Price: Your purchase/manufacturing cost\n• Current Price: Selling price to customers\n• Promotion %: Discount percentage when on sale"
        )
        pricing_main_layout.addWidget(pricing_explanation)

        # Pricing form
        pricing_title = QLabel("Pricing Controls")
        pricing_title.setStyleSheet("font-weight: bold; margin-top: 10px;")
        pricing_main_layout.addWidget(pricing_title)

        pricing_layout = QFormLayout()
        pricing_layout.setLabelAlignment(Qt.AlignRight)

        self.cost_val = self._create_money_field("Cost price paid for this product")
        self.price_val = self._create_money_field("Current selling price to customers")
        self.promo_chk = self._create_field(QCheckBox("On Promotion"), "Enable promotional pricing for this product")
        self.promo_val = self._create_field(QDoubleSpinBox(), "Promotional discount percentage (0-100%)")
        self.promo_val.setRange(0, 100)
        self.promo_val.setDecimals(2)

        pricing_layout.addRow("Cost Price:", self.cost_val)
        pricing_layout.addRow("Current Price:", self.price_val)
        pricing_layout.addRow("", self.promo_chk)
        pricing_layout.addRow("Promotion %:", self.promo_val)

        pricing_main_layout.addLayout(pricing_layout)

        # Actions section
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        self.save_btn = self._create_button("Save Changes", "Save all pricing changes to database")
        actions_layout.addWidget(self.save_btn)
        pricing_main_layout.addLayout(actions_layout)

        pricing_frame.setMinimumWidth(500)
        results_splitter.addWidget(pricing_frame)
        results_splitter.setSizes([400, 600])
        results_splitter.setStretchFactor(0, 2)
        results_splitter.setStretchFactor(1, 3)

        layout.addWidget(results_splitter)
        return tab

    def _create_sell_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(self._create_controls_frame("Sell Transaction"))
        
        # Transaction form
        form_frame, form_layout = self._create_form_section(
            "Sale Transaction",
            "💰 Product Sales", 
            "Process product sales by specifying the quantity to sell. The unit price is automatically calculated based on current pricing and any active promotions."
        )

        # Form fields
        form_fields = QFormLayout()
        form_fields.setLabelAlignment(Qt.AlignRight)

        self.sell_qty = self._create_field(QSpinBox(), "Number of units to sell to customer")
        self.sell_qty.setRange(1, 10**9)
        
        self.sell_price = QLabel("₪0.00")
        self.sell_price.setToolTip("Current selling price per unit (including promotions)")
        self.sell_price.setObjectName("PriceDisplay")

        form_fields.addRow("Quantity:", self.sell_qty)
        form_fields.addRow("Unit Price:", self.sell_price)

        form_layout.addLayout(form_fields)

        # Actions section
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        self.sell_btn = self._create_button("Process Sale", "Complete the sale transaction and update inventory")
        actions_layout.addWidget(self.sell_btn)
        form_layout.addLayout(actions_layout)
        form_layout.addStretch()

        layout.addWidget(form_frame)
        return tab

    def _create_buy_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(self._create_controls_frame("Purchase Transaction"))
        
        # Transaction form
        form_frame, form_layout = self._create_form_section(
            "Purchase Transaction",
            "📦 Inventory Replenishment",
            "Purchase additional inventory to restock this product. Specify the quantity to purchase from suppliers. The unit cost is based on your current cost price settings."
        )

        # Form fields
        form_fields = QFormLayout()
        form_fields.setLabelAlignment(Qt.AlignRight)

        self.buy_qty = self._create_field(QSpinBox(), "Number of units to purchase from supplier")
        self.buy_qty.setRange(1, 10**9)
        
        self.buy_cost = QLabel("₪0.00")
        self.buy_cost.setToolTip("Cost per unit for purchasing from supplier")
        self.buy_cost.setObjectName("PriceDisplay")

        form_fields.addRow("Quantity:", self.buy_qty)
        form_fields.addRow("Unit Cost:", self.buy_cost)

        form_layout.addLayout(form_fields)

        # Actions section
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        self.buy_btn = self._create_button("Purchase Stock", "Complete the purchase and add to inventory")
        actions_layout.addWidget(self.buy_btn)
        form_layout.addLayout(actions_layout)
        form_layout.addStretch()

        layout.addWidget(form_frame)
        return tab

    def _create_history_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(self._create_controls_frame("Transaction History"))
        layout.addWidget(self._create_explanation_section(
            "📊 Activity Timeline",
            "View complete transaction history and changes for this product. Track all sales, purchases, price changes, and inventory updates with timestamps for complete audit trail and business analytics."
        ))

        # History table
        table_frame = QFrame()
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(16, 16, 16, 16)
        
        table_title = QLabel("Transaction Log")
        table_title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        table_layout.addWidget(table_title)
        
        self.history_table = QTableWidget(0, 3)
        self.history_table.setHorizontalHeaderLabels(["Event Type", "Changes Made", "Date & Time"])
        self._cfg_table(self.history_table)
        
        # Add tooltips to table headers
        for i, tooltip in enumerate(["Type of transaction or change", "Details of what was modified", "When the change occurred"]):
            self.history_table.horizontalHeaderItem(i).setToolTip(tooltip)
        
        table_layout.addWidget(self.history_table)
        layout.addWidget(table_frame)
        return tab

    def _create_notes_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(self._create_controls_frame("Product Notes & Analysis"))
        layout.addWidget(self._create_explanation_section(
            "📝 Product Documentation",
            "Add notes and observations about this product for future reference. Use the analysis feature to get AI-powered insights about product performance, trends, and optimization recommendations."
        ))

        # Notes analysis section
        analysis_frame = QFrame()
        analysis_layout = QVBoxLayout(analysis_frame)
        analysis_layout.setContentsMargins(16, 16, 16, 16)
        
        analysis_title = QLabel("Analysis Results")
        analysis_title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        analysis_layout.addWidget(analysis_title)
        
        self.note_analyze = QTextEdit()
        self.note_analyze.setReadOnly(True)
        self.note_analyze.setPlaceholderText("Analysis results will appear here when you click 'Analyze Product'...")
        analysis_layout.addWidget(self.note_analyze)
        layout.addWidget(analysis_frame)

        # Note input section
        note_frame = QFrame()
        note_layout = QVBoxLayout(note_frame)
        note_layout.setContentsMargins(16, 12, 16, 12)
        
        input_title = QLabel("Add New Note")
        input_title.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        note_layout.addWidget(input_title)
        
        input_row_layout = QHBoxLayout()
        
        self.note_input = self._create_field(QLineEdit(), "Enter notes about product quality, supplier info, customer feedback, etc.")
        self.note_input.setPlaceholderText("Write a note about this product...")
        self.note_input.setFixedHeight(32)

        self.note_add_btn = self._create_button("Add Note", "Save this note to the product record")
        self.note_analyze_btn = self._create_button("Analyze Product", "Generate AI analysis of this product's performance and trends")

        input_row_layout.addWidget(self.note_input, 1)
        input_row_layout.addWidget(self.note_add_btn)
        input_row_layout.addWidget(self.note_analyze_btn)
        
        note_layout.addLayout(input_row_layout)
        layout.addWidget(note_frame)
        return tab

    def enable_add_mode(self) -> None:
        """Enable add mode - make fields editable for creating new product"""
        self.is_add_mode = True
        
        # Enable editing for product info fields
        self.product_id.setReadOnly(False)
        self.name_val.setReadOnly(False)
        self.brand_val.setReadOnly(False)
        self.category_val.setReadOnly(False)
        self.quantity_val.setReadOnly(False)
        
        # Clear all fields
        self.product_id.setText("")
        self.name_val.setText("")
        self.brand_val.setText("")
        self.category_val.setText("")
        self.quantity_val.setText("")
        self.cost_val.setValue(0.0)
        self.price_val.setValue(0.0)
        self.promo_chk.setChecked(False)
        self.promo_val.setValue(0.0)
        
        # Clear other tabs (styling handled by theme manager)
        self.buy_cost.setText("₪0.00")
        self.sell_price.setText("₪0.00")
        
        # Change save button text
        self.save_btn.setText("Create Product")
        
        # Change Add button to Back button
        self.add_btn.setText("← Back")
        
        # Update tab title to indicate add mode
        self.tabs.setTabText(0, "📋 Details & Pricing (Add Mode)")

    def disable_add_mode(self) -> None:
        """Disable add mode - make fields read-only for viewing existing product"""
        self.is_add_mode = False
        
        # Disable editing for product info fields
        self.product_id.setReadOnly(True)
        self.name_val.setReadOnly(True)
        self.brand_val.setReadOnly(True)
        self.category_val.setReadOnly(True)
        self.quantity_val.setReadOnly(True)
        
        # Change save button text back
        self.save_btn.setText("Save Changes")
        
        # Change Back button to Add button
        self.add_btn.setText("Add New")
        
        # Update tab title back to normal
        self.tabs.setTabText(0, "📋 Details & Pricing")

    def read_add_fields(self) -> dict:
        """Read all fields for creating a new product"""
        return {
            "product_id": self.product_id.text().strip(),
            "name": self.name_val.text().strip(),
            "brand": self.brand_val.text().strip() or None,
            "category": self.category_val.text().strip() or None,
            "quantity": int(self.quantity_val.text() or "0"),
            "current_price": float(self.price_val.value()),
            "cost_price": float(self.cost_val.value()),
            "is_on_promotion": bool(self.promo_chk.isChecked()),
            "promotion_discount_percent": float(self.promo_val.value()),
        }

    # ---------- Helpers for Presenter ----------
    def _cfg_table(self, t: QTableWidget) -> None:
        """Configure table with standard settings."""
        t.setAlternatingRowColors(True)
        t.setSelectionBehavior(QTableWidget.SelectRows)
        t.setSelectionMode(QTableWidget.SingleSelection)
        t.horizontalHeader().setStretchLastSection(True)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        t.verticalHeader().setVisible(False)
        t.setWordWrap(False)
        t.setEditTriggers(QTableWidget.NoEditTriggers)

    def read_edit_fields(self) -> dict:
        return {
            "current_price": float(self.price_val.value()),
            "cost_price": float(self.cost_val.value()),
            "is_on_promotion": bool(self.promo_chk.isChecked()),
            "promotion_discount_percent": float(self.promo_val.value()),
        }

    def set_details(self, product: dict) -> None:
        # If in add mode and we get empty data, don't override the current fields
        if self.is_add_mode and not product:
            return
            
        pid = str(product.get("product_id", "-"))
        name = str(product.get("name", ""))
        brand = str(product.get("brand") or "")
        category = str(product.get("category") or "")
        cost = float(product.get("cost_price") or 0)
        price = float(product.get("current_price") or 0)
        promo = bool(product.get("is_on_promotion"))
        promo_pct = float(product.get("promotion_discount_percent") or 0)
        quantity = int(product.get("quantity") or 0)
        note = str(product.get("note") or "Write a note about this product...")

        # Fill fields
        self.product_id.setText(pid)
        self.name_val.setText(name)
        self.brand_val.setText(brand)
        self.category_val.setText(category)
        self.cost_val.setValue(cost)
        self.price_val.setValue(price)
        self.promo_chk.setChecked(promo)
        self.promo_val.setValue(promo_pct)
        self.quantity_val.setText(str(quantity))
        self.note_input.setText(note)

        # Update price displays (styling handled by theme manager)
        self.buy_cost.setText(f"₪{cost:.2f}")
        self.sell_price.setText(f"₪{price:.2f}")

        self._original_values = {
            "current_price": price,
            "cost_price": cost,
            "is_on_promotion": promo,
            "promotion_discount_percent": promo_pct,
        }

    def set_history(self, events: List[dict]) -> None:
        self.history_table.setRowCount(0)
        for ev in events:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            when = datetime.fromisoformat(str(ev.get("occurred_at_utc") or "")).astimezone().strftime("%Y-%m-%d %H:%M:%S")
            etype = str(ev.get("event_type") or "")
            payload = ev.get("changes")
            payload_str = payload if isinstance(payload, str) else str(payload)
            for col, val in enumerate([etype, payload_str, when]):
                self.history_table.setItem(row, col, QTableWidgetItem(val))

    def set_back_mode(self, on_back_callback):
        """Configure the Add button as a Back button with callback."""
        self.add_btn.setText("← Back")
        self.add_btn.setToolTip("Return to previous view")
        # Disconnect existing functionality
        try:
            self.add_btn.clicked.disconnect()
        except:
            pass  # No connections to disconnect
        # Connect back functionality
        self.add_btn.clicked.connect(on_back_callback)

    def set_close_mode(self, on_close_callback):
        """Configure the close button and make it visible with callback."""
        self.close_btn.show()
        # Disconnect any existing functionality
        try:
            self.close_btn.clicked.disconnect()
        except:
            pass  # No connections to disconnect
        # Connect close functionality
        self.close_btn.clicked.connect(on_close_callback)
    
    # notifications
    def notify(self, text: str, title: str = "Info", *, critical: bool = False):
        if critical:
            return QMessageBox.critical(self, title, text)
        return QMessageBox.information(self, title, text)