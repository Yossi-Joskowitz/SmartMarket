# server/read_model/models.py
from dataclasses import dataclass
from typing import List, Optional
from common.db import get_conn

@dataclass
class ProductRead:
    product_id: str
    name: str
    price: float
    quantity: int
    is_deleted: bool
    updated_at: object  # datetime-like

class ProductReadModel:
    """
    Model that encapsulates data + DB access for read side (classic MVC).
    """
    @staticmethod
    def list_products(include_deleted: bool=False) -> List[ProductRead]:
        sql = (
            "SELECT ProductId, Name, Price, Quantity, IsDeleted, UpdatedAt "
            "FROM dbo.ProductsReadModel "
        )
        if not include_deleted:
            sql += "WHERE IsDeleted = 0 "
        sql += "ORDER BY Name ASC"

        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()

        return [
            ProductRead(
                product_id=row[0],
                name=row[1],
                price=float(row[2]),
                quantity=int(row[3]),
                is_deleted=bool(row[4]),
                updated_at=row[5],
            )
            for row in rows
        ]

    @staticmethod
    def get_product(product_id: str) -> Optional[ProductRead]:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT ProductId, Name, Price, Quantity, IsDeleted, UpdatedAt
                FROM dbo.ProductsReadModel
                WHERE ProductId = ?
                """,
                (product_id,),
            )
            row = cur.fetchone()

        if not row:
            return None

        return ProductRead(
            product_id=row[0],
            name=row[1],
            price=float(row[2]),
            quantity=int(row[3]),
            is_deleted=bool(row[4]),
            updated_at=row[5],
        )
