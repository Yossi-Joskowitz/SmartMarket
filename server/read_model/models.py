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
    brand: Optional[str]
    category: Optional[str]
    is_on_promotion: bool
    is_deleted: bool
    updated_at: object   


class ProductReadModel:
    """
    Model that encapsulates data + DB access for read side (classic MVC).
    """
    @staticmethod
    def list_products(
        *,
        query: Optional[str],
        category: Optional[str],
        brand: Optional[str],
        include_deleted: bool,
        limit: int,
        offset: int,
        sort_by: str,
        sort_dir: str,
    ) -> List[ProductRead]:
        sort_map = {
            "product_id": "ProductId",
            "name": "Name",
            "price": "Price",
            "quantity": "Quantity",
            "updated_at": "UpdatedAt",
        }
        order_col = sort_map.get((sort_by or "name").lower(), "Name")
        order_dir = "DESC" if (sort_dir or "asc").lower() == "desc" else "ASC"

        sql = [
            "SELECT ProductId, Name, Price, Quantity, Brand, Category, IsOnPromotion, IsDeleted, UpdatedAt",
            "FROM dbo.ProductsReadModel",
            "WHERE 1 = 1",
        ]
        params: List[object] = []

        if not include_deleted:
            sql.append("AND IsDeleted = 0")

        if category:
            sql.append("AND Category = ?")
            params.append(category)

        if brand:
            sql.append("AND Brand = ?")
            params.append(brand)

        if query:
            sql.append("AND (LOWER(ProductId) LIKE LOWER(?) OR LOWER(Name) LIKE LOWER(?))")
            like = f"%{query}%"
            params.extend([like, like])

        sql.append(f"ORDER BY {order_col} {order_dir}")
        sql.append("OFFSET ? ROWS FETCH NEXT ? ROWS ONLY")
        params.extend([offset, limit])

        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("\n".join(sql), params)
            rows = cur.fetchall()

        out: List[ProductRead] = []
        for r in rows:
            out.append(ProductRead(
                product_id=r[0],
                name=r[1],
                price=float(r[2]),
                quantity=int(r[3]),
                brand=r[4],
                category=r[5],
                is_on_promotion=bool(r[6]),
                is_deleted=bool(r[7]),
                updated_at=r[8],
            ))
        return out
    
    @staticmethod
    def get_product(product_id: str) -> Optional[ProductRead]:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT ProductId, Name, Price, Quantity, Brand, Category, IsOnPromotion, IsDeleted, UpdatedAt
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
            brand=row[4],
            category=row[5],
            is_on_promotion=bool(row[6]),
            is_deleted=bool(row[7]),
            updated_at=row[8],
        )
    
    @staticmethod
    def distinct_categories() -> List[str]:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT Category
                FROM dbo.ProductsReadModel
                WHERE IsDeleted = 0 AND Category IS NOT NULL AND LTRIM(RTRIM(Category)) <> ''
                ORDER BY Category
            """)
            return [r[0] for r in cur.fetchall()]

    @staticmethod
    def distinct_brands() -> List[str]:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT Brand
                FROM dbo.ProductsReadModel
                WHERE IsDeleted = 0 AND Brand IS NOT NULL AND LTRIM(RTRIM(Brand)) <> ''
                ORDER BY Brand
            """)
            return [r[0] for r in cur.fetchall()]

