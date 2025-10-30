from __future__ import annotations
from typing import Any, Dict, Optional
import os
import requests
from dotenv import load_dotenv
load_dotenv()


class PricingModel:
    def __init__(self, base_url: Optional[str] = None, timeout: float = 15.0) -> None:
        self.base_url = base_url or os.getenv("URL", "http://localhost:8000")
        self.session = requests.Session()
        self.timeout = timeout

    def get_product(self, product_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/query/products/{product_id}"
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def update_product(self, product_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/command/product/{product_id}/update"
        r = self.session.put(url, json=fields, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def change_price(self, product_id: str, *, current_price: Optional[float] = None, cost_price: Optional[float] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/command/product/{product_id}/change_price"
        fields = {}
        if current_price is not None:
            fields["current_price"] = current_price
        if cost_price is not None:
            fields["cost_price"] = cost_price
        r = self.session.post(url, params=fields, timeout=self.timeout)
        return r.json()

    def delete_product(self, product_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/command/product/{product_id}/delete"
        r = self.session.delete(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def create_product(self,product_id: str,name: str,current_price: float,cost_price: float,quantity: int,*,brand: Optional[str] = None,category: Optional[str] = None,is_on_promotion: bool = False,promotion_discount_percent: float = 0.0,
    ) -> Dict[str, Any]:
        """Create a new product via the server API"""
        url = f"{self.base_url}/command/product/create"
        payload = {
            "product_id": product_id,
            "name": name,
            "current_price": float(current_price),
            "cost_price": float(cost_price),
            "quantity": int(quantity),
            "brand": brand,
            "category": category,
            "is_on_promotion": 1 if is_on_promotion else 0,
            "promotion_discount_percent": float(promotion_discount_percent) if is_on_promotion else 0.0,
        }
        
        r = self.session.post(url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
        
    def sell(self, product_id: str, quantity_to_sell: int, sale_unit_price: float, sale_unit_cost: float) -> Dict[str, Any]:
        prod = self.get_product(product_id)
        current_qty = int(prod.get("quantity") or 0)
        if quantity_to_sell <= 0:
            raise RuntimeError("Quantity to sell must be > 0")
        if current_qty < quantity_to_sell:
            raise RuntimeError(f"Insufficient stock: have {current_qty}, need {quantity_to_sell}")
        url = f"{self.base_url}/command/product/{product_id}/sale"
        params = {"quantity": quantity_to_sell , "sale_unit_price": sale_unit_price, "sale_unit_cost": sale_unit_cost}
        r = self.session.post(url, params=params, timeout=self.timeout)
        return r.json()
        

    def purchase(self, product_id: str, quantity_to_buy: int, purchase_unit_cost: float) -> Dict[str, Any]:
        if quantity_to_buy <= 0:
            raise RuntimeError("Quantity to purchase must be > 0")
        url = f"{self.base_url}/command/product/{product_id}/purchase"
        params = {"quantity": quantity_to_buy , "purchase_unit_cost": purchase_unit_cost}
        r = self.session.post(url, params=params, timeout=self.timeout)
        return r.json()

    def get_events(self, product_id: str):
        url = f"{self.base_url}/query/products/{product_id}/events"
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def add_note(self, product_id: str, note: str):
        url = f"{self.base_url}/command/product/{product_id}/add_note"
        r = self.session.post(url, params={"note": note}, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def analyze_note(self,  note: str) -> Dict[str, Any]:
        url = f"{self.base_url}/chat/analyze_note"
        r = self.session.post(url, params={"note": note}, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
