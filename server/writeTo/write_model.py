from __future__ import annotations
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from common.db import get_conn 
import pyodbc

class EventType(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    PRICE_CHANGE = "PRICE_CHANGE"
    SALE = "SALE"
    PURCHASE = "PURCHASE"
    DELETE = "DELETE"
    NOTE_ADDED = "NOTE_ADDED"

def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)  

@dataclass
class Product:
    product_id: str
    name: Optional[str] = None
    current_price: Optional[float] = None
    cost_price: Optional[float] = None
    quantity: Optional[int] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    is_on_promotion: Optional[bool] = None
    promotion_discount_percent: Optional[float] = None
    image_url: Optional[str] = None
    note: Optional[str] = None

    # derived fields only in readProduct (not part of input on CREATE unless you really want to override)
    inventory_value: Optional[float] = None
    total_profit: Optional[float] = None

@dataclass
class Event:
    product_id: str
    event_type: EventType
    occurred_at_utc: datetime = field(default_factory=utcnow)
   
    # same "live" fields as readProduct, all optional/nullable in Events
    name: Optional[str] = None
    current_price: Optional[float] = None
    cost_price: Optional[float] = None
    quantity_after: Optional[int] = None
    quantity_delta: Optional[int] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    is_on_promotion: Optional[bool] = None
    promotion_discount_percent: Optional[float] = None
    image_url: Optional[str] = None
    note: Optional[str] = None

    # transactional extras
    sale_unit_price: Optional[float] = None
    sale_unit_cost: Optional[float] = None
    purchase_unit_cost: Optional[float] = None

    
@dataclass
class writeModel:

    @classmethod
    def create_product(self, p: Product, ev: Event) -> None:
        with get_conn() as cn:
            cur = cn.cursor()
            # Insert Event
            self._insert_event(cur, ev)

            # Insert readProduct initial row
            inventory_value = float(p.quantity or 0) * float(p.cost_price or 0.0)
            total_profit = 0.0

            cur.execute('''
                INSERT INTO readProduct (
                    product_id, name, current_price, cost_price, quantity,
                    brand, category, is_on_promotion, promotion_discount_percent,
                    image_url, note, inventory_value, total_profit, updated_at_utc
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSUTCDATETIME())
            ''',
            p.product_id, p.name, p.current_price, p.cost_price, p.quantity,
            p.brand, p.category, p.is_on_promotion or 0, p.promotion_discount_percent or 0.0,
            p.image_url, p.note, inventory_value, total_profit)
       
            cn.commit()

    @classmethod
    def update_product(self, fields: Dict[str, Any], ev: Event) -> None:
        with get_conn() as cn:
            cur = cn.cursor()
            self._insert_event(cur, ev)
            # Build UPDATE for readProduct dynamically
            set_parts = []
            params = []
            for k,v in fields.items():
                set_parts.append(f"{k} = ?")
                params.append(v)

            # Always bump updated_at_utc
            set_parts.append("updated_at_utc = SYSUTCDATETIME()")
            sql = f"UPDATE readProduct SET {', '.join(set_parts)} WHERE product_id = ?"
            params.append(ev.product_id)
            cur.execute(sql, params)
            cn.commit()
        

    @classmethod
    def change_price(self,ev: Event) -> None:

        with get_conn() as cn:
            cur = cn.cursor()
            self._insert_event(cur, ev)

            # Update readProduct values
            updates = []
            params = []
            if ev.current_price is not None:
                updates.append("current_price = ?")
                params.append(ev.current_price)
            if ev.cost_price is not None:
                updates.append("cost_price = ?")
                params.append(ev.cost_price)
            # Recompute inventory_value if cost_price changed
            if ev.cost_price is not None:
                updates.append("inventory_value = quantity * ?")
                params.append(ev.cost_price)

            updates.append("updated_at_utc = SYSUTCDATETIME()")
            sql = f"UPDATE readProduct SET {', '.join(updates)} WHERE product_id = ?"
            params.append(ev.product_id)
            cur.execute(sql, params)
            cn.commit()
    
    @classmethod
    def get_product_quantity_and_profit(self, product_id: str):
        with get_conn() as cn:
            cur = cn.cursor()
            cur.execute("SELECT quantity, total_profit FROM readProduct WHERE product_id = ?", product_id)
            row = cur.fetchone()
        if not row:
            return None
        return {
            "quantity": int(row[0]) if row[0] is not None else 0,
            "total_profit": float(row[1]) if row[1] is not None else 0.0,
        }


    @classmethod
    def get_product_quantity_cost_total_profit(self, product_id: str):
        with get_conn() as cn:
            cur = cn.cursor()
            cur.execute("SELECT quantity, cost_price, total_profit FROM readProduct WHERE product_id = ?", product_id)
            row = cur.fetchone()
        if not row:
            return None
        return {
            "quantity": int(row[0]) if row[0] is not None else 0,
            "cost_price": float(row[1]) if row[1] is not None else 0.0,
            "total_profit": float(row[2]) if row[2] is not None else 0.0,
        }

    @classmethod
    def purchase(self,ev: Event) -> None:

        with get_conn() as cn:
            cur = cn.cursor()
            self._insert_event(cur, ev)

            # Update readProduct
            cur.execute('''
                UPDATE readProduct
                SET quantity = ?, cost_price = ?, inventory_value = ? * ?,
                    updated_at_utc = ?
                WHERE product_id = ?
            ''', ev.quantity_after, ev.purchase_unit_cost, ev.quantity_after, ev.purchase_unit_cost, ev.occurred_at_utc, ev.product_id)

            cn.commit()


    @classmethod
    def sale(self, ev: Event, new_total_profit: float) -> None:

        with get_conn() as cn:
            cur = cn.cursor()
            self._insert_event(cur, ev)

            # Update readProduct (cost_price unchanged on SALE)
            inventory_value = ev.quantity_after * ev.cost_price
            cur.execute('''
                UPDATE readProduct
                SET quantity = ?, total_profit = ?, inventory_value = ?, updated_at_utc = SYSUTCDATETIME()
                WHERE product_id = ?
            ''', ev.quantity_after, new_total_profit, inventory_value, ev.product_id)
            cn.commit()

    @classmethod
    def set_promotion(self, ev: Event) -> None:
        with get_conn() as cn:
            cur = cn.cursor()
            self._insert_event(cur, ev)
            cur.execute('''
                UPDATE readProduct
                SET is_on_promotion = ?, promotion_discount_percent = ?, updated_at_utc = SYSUTCDATETIME()
                WHERE product_id = ?
            ''', 1 if ev.is_on_promotion else 0, ev.promotion_discount_percent, ev.product_id)
            cn.commit()
    
    @classmethod
    def add_note(self, ev: Event) -> None:

        with get_conn() as cn:
            cur = cn.cursor()
            self._insert_event(cur, ev)
            cur.execute('''
                UPDATE readProduct SET note = ?, updated_at_utc = SYSUTCDATETIME()
                WHERE product_id = ?
            ''', ev.note, ev.product_id)
            cn.commit()
       
    @classmethod
    def delete_product(self, ev: Event) -> None:
        with get_conn() as cn:
            cur = cn.cursor()
            self._insert_event(cur, ev)
            cur.execute("DELETE FROM readProduct WHERE product_id = ?", ev.product_id)
            cn.commit()

    @staticmethod
    def _insert_event(cur: pyodbc.Cursor, ev: Event) -> None:
        # Keep parameter order aligned with schema columns
        cur.execute('''
            INSERT INTO Events (
                product_id, event_type, occurred_at_utc,
                name, current_price, cost_price, quantity_after, quantity_delta,
                brand, category, is_on_promotion, promotion_discount_percent,
                image_url, note, sale_unit_price, sale_unit_cost, purchase_unit_cost
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        ev.product_id, ev.event_type.value, ev.occurred_at_utc,
        ev.name, ev.current_price, ev.cost_price, ev.quantity_after, ev.quantity_delta,
        ev.brand, ev.category, ev.is_on_promotion, ev.promotion_discount_percent,
        ev.image_url, ev.note, ev.sale_unit_price, ev.sale_unit_cost, ev.purchase_unit_cost)

    @classmethod
    def upload_image(self, ev: Event) -> None:
        with get_conn() as cn:
            cur = cn.cursor()
            self._insert_event(cur, ev)
            cur.execute('''
                UPDATE readProduct
                SET image_url = ?, updated_at_utc = SYSUTCDATETIME()
                WHERE product_id = ?
            ''', ev.image_url, ev.product_id)
            cn.commit()
