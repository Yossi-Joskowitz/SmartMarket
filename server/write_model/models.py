from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
import json
from common.db import get_conn  


@dataclass
class Product:
    product_id: str
    name: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    is_deleted: bool = False

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
                prod.is_deleted = False

            elif event_type == "ProductUpdated":
                if "name" in data and data["name"] is not None:
                    prod.name = data["name"]
                if "price" in data and data["price"] is not None:
                    prod.price = float(data["price"])
                if "quantity" in data and data["quantity"] is not None:
                    prod.quantity = int(data["quantity"])

            elif event_type == "ProductDeleted":
                prod.is_deleted = True

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
        pid = data["product_id"]
        name = data.get("name")
        price = data.get("price")
        quantity = data.get("quantity")

        if event_type == "ProductCreated":
            cur.execute(
                """
                MERGE dbo.ProductsReadModel AS T
                USING (SELECT ? AS ProductId) AS S
                ON T.ProductId = S.ProductId
                WHEN MATCHED THEN UPDATE SET
                    Name = ?, Price = ?, Quantity = ?, IsDeleted = 0, UpdatedAt = SYSUTCDATETIME()
                WHEN NOT MATCHED THEN INSERT (ProductId, Name, Price, Quantity, IsDeleted, UpdatedAt)
                VALUES (?, ?, ?, ?, 0, SYSUTCDATETIME());
                """,
                (pid, name, price, quantity, pid, name, price, quantity)
            )

        elif event_type == "ProductUpdated":
            cur.execute(
                """
                UPDATE dbo.ProductsReadModel
                SET Name     = COALESCE(?, Name),
                    Price    = COALESCE(?, Price),
                    Quantity = COALESCE(?, Quantity),
                    UpdatedAt = SYSUTCDATETIME()
                WHERE ProductId = ? AND IsDeleted = 0
                """,
                (name, price, quantity, pid)
            )

        elif event_type == "ProductDeleted":
            cur.execute(
                """
                UPDATE dbo.ProductsReadModel
                SET IsDeleted = 1, UpdatedAt = SYSUTCDATETIME()
                WHERE ProductId = ?
                """,
                (pid,)
            )
