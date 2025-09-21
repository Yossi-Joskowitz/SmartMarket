from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
import json
from common.db import get_conn  
from datetime import datetime


@dataclass
class Product:
    product_id: str
    name: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    is_on_promotion: bool = False
    is_deleted: bool = False
    updated_at: Optional[datetime] = None

    # --------------------------
    @classmethod
    def load(cls, product_id: str) -> "Product":
        prod = cls(product_id=product_id)
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT EventType, EventData
                FROM dbo.Events
                WHERE AggregateId = ?
                ORDER BY Id ASC
                """,
                (product_id,)
            )
            rows = cur.fetchall()

        for event_type, data_json in rows:
            data = json.loads(data_json)
            if event_type == "ProductCreated":
                prod.name = data["name"]
                prod.price = float(data["price"])
                prod.quantity = int(data["quantity"])
                prod.brand = data.get("brand")
                prod.category = data.get("category")
                prod.is_on_promotion = data.get("is_on_promotion", False)
                prod.updated_at = datetime.utcnow()
                prod.is_deleted = False

            elif event_type == "ProductUpdated":
                if "name" in data and data["name"] is not None:
                    prod.name = data["name"]
                if "price" in data and data["price"] is not None:
                    prod.price = float(data["price"])
                if "quantity" in data and data["quantity"] is not None:
                    prod.quantity = int(data["quantity"])
                if "brand" in data and data["brand"] is not None:
                    prod.brand = data["brand"]
                if "category" in data and data["category"] is not None:
                    prod.category = data["category"]
                if "is_on_promotion" in data:
                    prod.is_on_promotion = bool(data["is_on_promotion"])
                prod.updated_at = datetime.utcnow()

            elif event_type == "ProductDeleted":
                prod.is_deleted = True
                prod.updated_at = datetime.utcnow()

        return prod

    # --------------------------
    def commit_event(self, event_type: str, data: Dict[str, Any]) -> None:

        payload = json.dumps(data)
        product_id = self.product_id

        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO dbo.Events (AggregateId, EventType, EventData)
                VALUES (?, ?, ?)
                """,
                (product_id, event_type, payload)
            )
            self._project_to_read_model(cur, event_type, data)
            conn.commit()


    def _project_to_read_model(self, cur, event_type: str, data: Dict[str, Any]) -> None:
        product_id = data["product_id"]
        name = data.get("name")
        price = data.get("price")
        quantity = data.get("quantity")
        brand = data.get("brand")
        category = data.get("category")
        is_on_promotion = data.get("is_on_promotion", 0)
        
        if event_type == "ProductCreated":
            cur.execute(
                """
                MERGE dbo.ProductsReadModel AS T
                USING (SELECT ? AS ProductId) AS S
                ON T.ProductId = S.ProductId
                WHEN MATCHED THEN UPDATE SET
                    Name = ?, Price = ?, Quantity = ?, Brand = ?, Category = ?, IsOnPromotion = ?, 
                    IsDeleted = 0, UpdatedAt = SYSUTCDATETIME()
                WHEN NOT MATCHED THEN INSERT (ProductId, Name, Price, Quantity, Brand, Category, IsOnPromotion, IsDeleted, UpdatedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, SYSUTCDATETIME());
                """,
                (product_id, name, price, quantity, brand, category, is_on_promotion,
                product_id, name, price, quantity, brand, category, is_on_promotion)
            )

        elif event_type == "ProductUpdated":
            cur.execute(
                """
                UPDATE dbo.ProductsReadModel
                SET Name = COALESCE(?, Name),
                    Price = COALESCE(?, Price),
                    Quantity = COALESCE(?, Quantity),
                    Brand = COALESCE(?, Brand),
                    Category = COALESCE(?, Category),
                    IsOnPromotion = COALESCE(?, IsOnPromotion),
                    UpdatedAt = SYSUTCDATETIME()
                WHERE ProductId = ? AND IsDeleted = 0
                """,
                (name, price, quantity, brand, category, is_on_promotion, product_id)
            )

        elif event_type == "ProductDeleted":
            cur.execute(
                """
                UPDATE dbo.ProductsReadModel
                SET IsDeleted = 1, UpdatedAt = SYSUTCDATETIME()
                WHERE ProductId = ?
                """,
                (product_id,)
            )
