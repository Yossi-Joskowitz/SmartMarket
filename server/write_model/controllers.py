"""
WriteController: כללי עסקים + אורקסטרציה.
המודל (Product) מבצע את העבודה בפועל דרך commit_event().
"""
from typing import Optional
from .models import Product


class WriteController:
    def __init__(self):
        pass

    def create_product(self, product_id: str, name: str, price: float, quantity: int) -> dict:
        if price < 0 or quantity < 0:
            raise ValueError("Price/Quantity must be non-negative")
        
        agg = Product.load(product_id)
        if agg.name is not None and not agg.is_deleted:
            raise ValueError("Product already exists")

        event = {
            "product_id": product_id,
            "name": name,
            "price": float(price),
            "quantity": int(quantity),
        }

        agg.commit_event("ProductCreated", event)

        return {"ok": True}

    def update_product(self, product_id: str,name: Optional[str],price: Optional[float],
                       quantity: Optional[int]) -> dict:
        if price is not None and price < 0:
            raise ValueError("Price must be non-negative")
        if quantity is not None and quantity < 0:
            raise ValueError("Quantity must be non-negative")
        
        agg = Product.load(product_id)
        if agg.name is None or agg.is_deleted:
            raise ValueError("Product does not exist or is deleted")

        event = {
            "product_id": product_id,
            "name": name,
            "price": float(price) if price is not None else None,
            "quantity": int(quantity) if quantity is not None else None,
        }

        agg.commit_event("ProductUpdated", event)

        return {"ok": True}

    def delete_product(self, product_id: str) -> dict:
        agg = Product.load(product_id)

        if agg.name is None or agg.is_deleted:
            raise ValueError("Product does not exist or already deleted")

        event = {"product_id": product_id}

        agg.commit_event("ProductDeleted", event)

        return {"ok": True}
