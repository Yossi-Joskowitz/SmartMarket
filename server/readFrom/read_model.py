# server/read_model/models.py
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json
from common.db import get_conn

@dataclass
class ProductRead:
    product_id: str
    name: str
    current_price: float
    quantity: int
    cost_price: Optional[float] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    is_on_promotion: bool = False
    promotion_discount_percent: Optional[float] = 0.0
    note: Optional[str] = None
    updated_at_utc: object = None


class ReadModel:
    """
    Model that encapsulates data + DB access for read side (classic MVC).
    """
    @staticmethod
    def list_products(*,query: Optional[str],category: Optional[str],brand: Optional[str]) -> List[ProductRead]:
        sql = [
            "SELECT product_id, name, current_price, quantity, is_on_promotion",
            "FROM dbo.readProduct",
            "WHERE 1 = 1",
        ]
        params: List[object] = []

        if category:
            sql.append("AND category = ?")
            params.append(category)

        if brand:
            sql.append("AND brand = ?")
            params.append(brand)

        if query:
            sql.append("AND (LOWER(product_id) LIKE LOWER(?) OR LOWER(name) LIKE LOWER(?))")
            like = f"%{query}%"
            params.extend([like, like])


        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("\n".join(sql), params)
            rows = cur.fetchall()

        out: List[ProductRead] = []
        for r in rows:
            out.append(ProductRead(
                product_id=r[0],
                name=r[1],
                current_price=float(r[2]),
                quantity=int(r[3]),
                is_on_promotion=bool(r[4]),
            ))
        return out
    
    @staticmethod
    def get_product(product_id: str) -> Optional[ProductRead]:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT product_id, name, current_price, cost_price, quantity, brand, category, is_on_promotion, promotion_discount_percent, note, updated_at_utc
                FROM dbo.readProduct
                WHERE product_id = ?
                """,
                (product_id,),
            )
            row = cur.fetchone()

        if not row:
            return None

        return ProductRead(
            product_id=row[0],
            name=row[1],
            current_price=float(row[2]),
            cost_price=float(row[3]) if row[3] is not None else None,
            quantity=int(row[4]),
            brand=row[5],
            category=row[6],
            is_on_promotion=bool(row[7]),
            promotion_discount_percent=float(row[8]) if row[8] is not None else None,
            note=row[9],
            updated_at_utc=row[10],
        )

    @staticmethod
    def distinct_categories() -> List[str]:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT Category
                FROM dbo.readProduct
                WHERE Category IS NOT NULL AND LTRIM(RTRIM(Category)) <> ''
                ORDER BY Category
            """)
            return [r[0] for r in cur.fetchall()]

    @staticmethod
    def distinct_brands() -> List[str]:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT Brand
                FROM dbo.readProduct
                WHERE  Brand IS NOT NULL AND LTRIM(RTRIM(Brand)) <> ''
                ORDER BY Brand
            """)
            return [r[0] for r in cur.fetchall()]


    @staticmethod
    def product_events(product_id: str) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []

        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT 
                    event_id, product_id, event_type, occurred_at_utc,
                    name, current_price, cost_price,
                    quantity_after, quantity_delta,
                    brand, category, is_on_promotion,
                    promotion_discount_percent, note
                FROM dbo.Events
                WHERE product_id = ?
                ORDER BY event_id ASC
                """,
                (product_id,)
            )
            rows = cur.fetchall()

        # נבנה לכל שורה מילון עם הנתונים שרלוונטיים
        for (
            event_id, product_id, event_type, occurred_at_utc,
            name, current_price, cost_price,
            quantity_after, quantity_delta,
            brand, category, is_on_promotion,
            promotion_discount_percent, note
        ) in rows:

            changes = {}

            # נוסיף רק שדות שאינם None (כלומר שדה שעודכן)
            if name is not None:
                changes["name"] = name
            if current_price is not None:
                changes["current_price"] = float(current_price)
            if cost_price is not None:
                changes["cost_price"] = float(cost_price)
            if quantity_after is not None:
                changes["quantity_after"] = int(quantity_after)
            if quantity_delta is not None:
                changes["quantity_delta"] = int(quantity_delta)
            if brand is not None:
                changes["brand"] = brand
            if category is not None:
                changes["category"] = category
            if is_on_promotion is not None:
                changes["is_on_promotion"] = bool(is_on_promotion)
            if promotion_discount_percent is not None:
                changes["promotion_discount_percent"] = float(promotion_discount_percent)
            if note is not None:
                changes["note"] = note

            events.append({
                "event_type": event_type,
                "occurred_at_utc": occurred_at_utc,
                "changes": changes
            })

        return events

    @staticmethod
    def get_products_profit() -> List[Dict[str, Any]]:
        profits: List[Dict[str, Any]] = []
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT name, total_profit
                FROM dbo.readProduct
                """
            )
            rows = cur.fetchall()
        for name, total_profit in rows:
            profits.append({
                "name": name,
                "total_profit": float(total_profit) if total_profit is not None else 0.0
            })

        return profits
    
    @staticmethod
    def get_products_category_value() -> List[Dict[str, Any]]:
        category_values: List[Dict[str, Any]] = []
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT 
                    category,
                    COUNT(DISTINCT product_id) AS total_products,
                    SUM(inventory_value) AS total_inventory_value
                FROM dbo.readProduct
                GROUP BY category;
                """
            )
            rows = cur.fetchall()
        for category, total_quantity, total_inventory_value in rows:
            category_values.append({
                "category": category,
                "total_quantity": int(total_quantity) if total_quantity is not None else 0,
                "total_inventory_value": float(total_inventory_value) if total_inventory_value is not None else 0.0
            })

        return category_values
    
    @staticmethod
    def get_products_total_profit_per_month() -> List[Dict[str, Any]]:
        monthly_profits: List[Dict[str, Any]] = []
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                WITH sales AS (
                    SELECT
                        YEAR(occurred_at_utc)  AS profit_year,
                        MONTH(occurred_at_utc) AS profit_month,
                        -- מכירה אמורה להיות quantity_delta שלילי, ממירים לכמות חיובית:
                        CAST(CASE WHEN quantity_delta < 0 THEN -quantity_delta ELSE quantity_delta END AS float) AS qty,
                        COALESCE(sale_unit_price, 0.0) AS sale_price,
                        COALESCE(cost_price,      0.0) AS unit_cost
                    FROM dbo.Events
                    WHERE event_type = 'SALE'
                )
                SELECT
                    profit_year,
                    profit_month,
                    SUM(qty * (sale_price - unit_cost)) AS total_profit
                FROM sales
                GROUP BY profit_year, profit_month
                ORDER BY profit_year, profit_month;
                """
            )
            rows = cur.fetchall()
        for profit_year, profit_month, total_profit in rows:
            monthly_profits.append({
                "year": int(profit_year),
                "month": int(profit_month),
                "total_profit": float(total_profit) if total_profit is not None else 0.0
            })

        return monthly_profits
    
    @staticmethod
    def get_product_image(product_id: str):
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT image_url FROM dbo.readProduct WHERE product_id = ?", (product_id,))
            row = cur.fetchone()

        return row[0].strip() if row and row[0] and str(row[0]).strip() else None