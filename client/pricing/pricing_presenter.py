from __future__ import annotations
from typing import Optional, Dict, Any
from .pricing_view import PricingView
from .pricing_model import PricingModel
from thread_manager import run_in_worker


class PricingPresenter:
    def __init__(self, view: PricingView, model: PricingModel, product_id: Optional[str] = None, close_callback=None) -> None:
        self.v = view
        self.m = model
        self.current_product_id: Optional[str] = product_id
        self.close_callback = close_callback
        
        # Wire UI events        
        self.v.refresh_btn.clicked.connect(self.reload_all)
        self.v.load_btn.clicked.connect(self.on_load_product)
        self.v.add_btn.clicked.connect(self.on_add_product)
        self.v.save_btn.clicked.connect(self.on_save)
        self.v.delete_btn.clicked.connect(self.on_delete)
        self.v.sell_btn.clicked.connect(self.on_sell)
        self.v.buy_btn.clicked.connect(self.on_purchase)
        self.v.note_add_btn.clicked.connect(self.on_add_note)
        self.v.note_analyze_btn.clicked.connect(self.on_analyze_note)

        # Set up close button if callback provided
        if self.close_callback:
            self.v.set_close_mode(self.close_callback)

        # Initial
        if self.current_product_id:
            try:
                self.v.product_id_input.setText(self.current_product_id)
            except Exception:
                pass
            self.reload_all()

    # ---------- Loads ----------
    def on_load_product(self) -> None:
        self.current_product_id = self.v.product_id_input.text().strip()
        if not self.current_product_id:
            return
        
        # Exit add mode when loading existing product
        if self.v.is_add_mode:
            self.v.disable_add_mode()
            
        try:
            self.v.product_id_input.setText(self.current_product_id)
        except Exception:
            pass
        self.reload_all()

    def reload_all(self) -> None:
        if not self.current_product_id:
            return

        @run_in_worker
        def load():
            prod = self.m.get_product(self.current_product_id)
            try:
                events = self.m.get_events(self.current_product_id)
            except Exception:
                events = []
            notes = []  
            return {"product": prod, "events": events, "notes": notes}

        def on_result(data: Dict[str, Any]):
            self.v.set_details(data["product"])
            self.v.set_history(data["events"])

        load(on_result=on_result, on_error=self._show_error)

    # ---------- Actions ----------
    def on_add_product(self) -> None:
        """Handle Add/Back button click - toggle between add mode and normal mode"""
        if self.v.is_add_mode:
            # Currently in add mode, so go back to normal mode
            self.v.disable_add_mode()
            # Clear fields and reset to empty state
            self.current_product_id = None
            self.v.product_id_input.setText("")
            self.v.set_details({})
            self.v.set_history([])
        else:
            # Currently in normal mode, so enable add mode for creating new product
            self.current_product_id = None
            self.v.product_id_input.setText("")
            self.v.enable_add_mode()
            self.v.set_history([])

    def on_save(self) -> None:
        if self.v.is_add_mode:
            # Handle creating new product
            try:
                fields = self.v.read_add_fields()
                
                # Validate required fields
                if not fields["product_id"]:
                    self.v.notify("Product ID is required.", "Validation Error", critical=True)
                    return
                if not fields["name"]:
                    self.v.notify("Product name is required.", "Validation Error", critical=True)
                    return
                if fields["current_price"] < 0 or fields["cost_price"] < 0:
                    self.v.notify("Prices cannot be negative.", "Validation Error", critical=True)
                    return
                if fields["quantity"] < 0:
                    self.v.notify("Quantity cannot be negative.", "Validation Error", critical=True)
                    return
                
                @run_in_worker
                def do():
                    return self.m.create_product(
                        product_id=fields["product_id"],
                        name=fields["name"],
                        current_price=fields["current_price"],
                        cost_price=fields["cost_price"],
                        quantity=fields["quantity"],
                        brand=fields["brand"],
                        category=fields["category"],
                        is_on_promotion=fields["is_on_promotion"],
                        promotion_discount_percent=fields["promotion_discount_percent"],
                    )

                def done(_):
                    # Switch to view mode and load the new product
                    self.current_product_id = fields["product_id"]
                    self.v.product_id_input.setText(fields["product_id"])
                    self.v.disable_add_mode()
                    self.reload_all()
                    self.v.notify(f"Product '{fields['product_id']}' created successfully.")

                do(on_result=done, on_error=self._show_error)
                
            except ValueError as e:
                self.v.notify(f"Invalid input: {e}", "Validation Error", critical=True)
                
        else:
            # Handle updating existing product
            fields = self.v.read_edit_fields()

            fields = {k: v for k, v in fields.items() if k in self.v._original_values and v != self.v._original_values[k]}

            change_price = {}
            if "current_price" in fields:
                change_price["current_price"] = fields["current_price"]
            if "cost_price" in fields:
                change_price["cost_price"] = fields["cost_price"]

            pid = self.current_product_id
            if not pid:
                return
        
            @run_in_worker
            def do():
                if change_price:
                    self.m.change_price(pid, **change_price)
                    for k in change_price.keys():
                        fields.pop(k, None)
                return self.m.update_product(pid, fields)

            def done(_):
                self.reload_all()
                self.v.notify(f"Product '{pid}' updated.")

            do(on_result=done, on_error=self._show_error)

    def on_delete(self) -> None:
        if not self.current_product_id:
            return
        pid = self.current_product_id
        @run_in_worker
        def do():
            return self.m.delete_product(pid)

        def done(_):
            self.current_product_id = None
            self.v.product_id_input.setText("")
            self.v.set_details({})
            self.v.set_history([])
            self.v.notify(f"Product '{pid}' deleted.")

        do(on_result=done, on_error=self._show_error)

    def on_sell(self) -> None:
        qty = int(self.v.sell_qty.value())
        
        if not self.current_product_id:
            return
        pid = self.current_product_id

        @run_in_worker
        def do():
            return self.m.sell(pid, qty ,self.v.price_val.value(),self.v.cost_val.value())
        def done(_):
            self.reload_all()
            self.v.notify(f"Product '{pid}' sold.")

        do(on_result=done, on_error=self._show_error)

    def on_purchase(self) -> None:
        qty = int(self.v.buy_qty.value())
        
        if not self.current_product_id:
            return
        pid = self.current_product_id

        @run_in_worker
        def do():
            return self.m.purchase(pid, qty,self.v.cost_val.value())

        def done(_):
            self.reload_all()
            self.v.notify(f"Product '{pid}' purchased.")

        do(on_result=done, on_error=self._show_error)

    # Notes not implemented -> no-ops with refresh
    def on_add_note(self) -> None:
        text = self.v.note_input.text().strip()
        if not text:
            return
        if not self.current_product_id:
            return

        @run_in_worker
        def do():
            return self.m.add_note(self.current_product_id,text)

        def done(_):
            self.reload_all()
            self.v.notify(f"Product '{self.current_product_id}' note added.")

        do(on_result=done, on_error=self._show_error)
    
    
    def on_analyze_note(self) -> None:
        if not self.current_product_id:
            self.v.notify("No product loaded.", "Error", critical=True)
            return

        if self.v.note_input.text().strip() == "Write a note about this product...":
            self.v.notify("Please enter a note to analyze.", "Error", critical=True)
            return
        @run_in_worker
        def do():
            return self.m.analyze_note(self.v.note_input.text().strip())
        def done(result):
            data = result
            text = (
                f"🧠 Sentiment Breakdown:\n"
                f"  • Neutral: {data['sentiment_breakdown']['neutral']}%\n"
                f"  • Positive: {data['sentiment_breakdown']['positive']}%\n"
                f"  • Negative: {data['sentiment_breakdown']['negative']}%\n\n"
                f"🏷️ Tag: {data['tag']}\n\n"
                f"💬 Summary:\n{data['summary']}"
            )

            self.v.note_analyze.setText(text)
        do(on_result=done, on_error=self._show_error)


    # ---------- Utilities ----------
    def _show_error(self, e: Exception) -> None:
        self.v.notify(f"Operation Failed: {e}", "Error", critical=True)
        

# Factory
def create_pricing_page(product_id: Optional[str] = None, base_url: Optional[str] = None, close_callback=None) -> PricingView:
    view = PricingView()
    model = PricingModel(base_url=base_url)
    view.presenter = PricingPresenter(view, model, product_id=product_id, close_callback=close_callback)
    return view
