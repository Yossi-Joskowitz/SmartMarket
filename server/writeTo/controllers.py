from __future__ import annotations
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from typing import Optional, Dict, Any
from .write_model import Event, EventType, Product, writeModel




class writeController:

    def ensure_valid_for_type(self, ev: Event) -> None:
        # Minimal guardrails; keep simple.
        if ev.event_type == EventType.SALE:
            if ev.quantity_delta is None or ev.quantity_delta >= 0:
                raise ValueError("SALE requires quantity_delta < 0")
            if ev.sale_unit_price is None or ev.sale_unit_cost is None:
                raise ValueError("SALE requires sale_unit_price and sale_unit_cost")
        if ev.event_type == EventType.PURCHASE:
            if ev.quantity_delta is None or ev.quantity_delta <= 0:
                raise ValueError("PURCHASE requires quantity_delta > 0")
            if ev.purchase_unit_cost is None:
                raise ValueError("PURCHASE requires purchase_unit_cost")
        if ev.event_type == EventType.PRICE_CHANGE:
            if ev.current_price is None and ev.cost_price is None:
                raise ValueError("PRICE_CHANGE requires current_price and/or cost_price")
        if ev.event_type == EventType.CREATE:
            # Allow CREATE to rely on quantity_after (initial stock); quantity_delta is optional here.
            if not ev.product_id or not ev.name or ev.current_price is None or ev.cost_price is None or ev.quantity_after is None:
                # Allow very simple but sensible CREATE.
                raise ValueError("CREATE requires name, current_price, cost_price, quantity")


    # --- Public API (writing methods) ---
    def create_product(self, p: Product) -> None:
        # Create event + initialize readProduct row.
        ev = Event(
            product_id=p.product_id,
            event_type=EventType.CREATE,
            name=p.name,
            current_price=p.current_price,
            cost_price=p.cost_price,
            quantity_after=p.quantity,
            quantity_delta=None,
            brand=p.brand,
            category=p.category,
            is_on_promotion=p.is_on_promotion,
            promotion_discount_percent=p.promotion_discount_percent,
            image_url=p.image_url,
            note=p.note,
        )
        self.ensure_valid_for_type(ev)
        writeModel.create_product(p, ev)

    def update_product(self, product_id: str, fields: Dict[str, Any]) -> None:
        allowed = {"name","brand","category","image_url","is_on_promotion","promotion_discount_percent","note"}
        fields = {k:v for k,v in fields.items() if k in allowed}
        if not fields:
            return

        ev = Event(product_id=product_id, event_type=EventType.UPDATE)
        for k,v in fields.items():
            setattr(ev, k if k!="image_url" else "image_url", v)

        writeModel.update_product(fields, ev)
        


    def change_price(self, product_id: str, *, current_price: Optional[float] = None, cost_price: Optional[float] = None) -> None:
        if current_price is None and cost_price is None:
            return

        ev = Event(
            product_id=product_id,
            event_type=EventType.PRICE_CHANGE,
            current_price=current_price,
            cost_price=cost_price,
        )
        self.ensure_valid_for_type(ev)

        writeModel.change_price(ev)



    def purchase(self, product_id: str, quantity: int, purchase_unit_cost: float,
                 actor: Optional[str]=None, reference_id: Optional[str]=None) -> None:
        # PURCHASE: quantity_delta > 0, update average cost_price, quantity, inventory_value
        if quantity <= 0:
            raise ValueError("PURCHASE quantity must be > 0")

        row = writeModel.get_product_quantity_and_cost(product_id)
        if not row:
            print(f"Product {product_id} not found")
        cur_qty, cur_cost = row['quantity'], float(row['cost_price'] or 0.0)
        # Weighted average cost
        new_qty = cur_qty + quantity
        if new_qty <= 0:
            # edge guard (shouldn't happen on PURCHASE)
            new_cost = purchase_unit_cost
        else:
            total_cost_before = cur_qty * cur_cost
            total_cost_purchase = quantity * purchase_unit_cost
            new_cost = (total_cost_before + total_cost_purchase) / new_qty
        # Insert event
        ev = Event(
            product_id=product_id,
            event_type=EventType.PURCHASE,
            quantity_delta=quantity,
            quantity_after=new_qty,
            purchase_unit_cost=purchase_unit_cost,
            cost_price=new_cost,  # optional reflection in event
        )
        self.ensure_valid_for_type(ev)
        writeModel.purchase(ev)
       
        

    def sale(self, product_id: str, quantity: int, sale_unit_price: float, sale_unit_cost: float) -> None:
        # SALE: quantity_delta < 0, update quantity, total_profit += qty * (price - cost), inventory_value = quantity * cost_price
        if quantity <= 0:
            raise ValueError("SALE quantity must be > 0")

        row = writeModel.get_product_quantity_cost_total_profit(product_id)
        if not row:
            raise ValueError(f"Product {product_id} not found")
        cur_qty = int(row["quantity"])  # dict keys from writeModel
        cost_price = float(row["cost_price"] or 0.0)
        total_profit = float(row["total_profit"] or 0.0)

        if quantity > cur_qty:
            raise ValueError(f"SALE quantity {quantity} exceeds current stock {cur_qty}")

        new_qty = cur_qty - quantity
        profit_delta = quantity * (float(sale_unit_price) - float(sale_unit_cost))
        new_total_profit = total_profit + profit_delta

        # Insert event
        ev = Event(
            product_id=product_id,
            event_type=EventType.SALE,
            quantity_delta=-quantity,
            quantity_after=new_qty,
            sale_unit_price=sale_unit_price,
            sale_unit_cost=sale_unit_cost,
            cost_price=cost_price,
        )
        self.ensure_valid_for_type(ev)
        writeModel.sale(ev,new_total_profit)

    def set_promotion(self, product_id: str, *, is_on_promotion: bool, promotion_discount_percent: float,
                      ) -> None:
        ev = Event(
            product_id=product_id,
            event_type=EventType.UPDATE,
            is_on_promotion=is_on_promotion,
            promotion_discount_percent=promotion_discount_percent,
        )
        writeModel.set_promotion(ev)

    def add_note(self, product_id: str, note: str) -> None:
        ev = Event(
            product_id=product_id,
            event_type=EventType.NOTE_ADDED,
            note=note
        )
        writeModel.add_note(ev)

    def delete_product(self, product_id: str) -> None:
        ev = Event(product_id=product_id, event_type=EventType.DELETE)
        writeModel.delete_product(ev)


