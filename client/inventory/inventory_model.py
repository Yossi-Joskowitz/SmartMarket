from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import os
import requests
from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv("URL", "http://localhost:8000")

@dataclass
class ReadProduct:
    product_id: str
    name: str
    current_price: float
    quantity: int
    is_on_promotion: bool = False
    brand: Optional[str] = None
    category: Optional[str] = None

    @staticmethod
    def from_json(j: Dict[str, Any]) -> "ReadProduct":
        return ReadProduct(
            product_id=j.get("product_id", ""),
            name=j.get("name", ""),
            current_price=float(j.get("current_price", 0.0)),
            quantity=int(j.get("quantity", 0)),
            is_on_promotion=bool(j.get("is_on_promotion", j.get("IsOnPromotion", False)))
        )


class InventoryModel:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or BASE_URL
        self.s = requests.Session()

    # ---------- Queries ----------
    def list_products(self, *, query: Optional[str] = None, category: Optional[str] = None, brand: Optional[str] = None,) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/query/products"
        params: Dict[str, Any] = {}
        if query:    params["q"] = query          
        if category: params["category"] = category
        if brand:    params["brand"] = brand

        r = self.s.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def get_product(self, product_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/query/products/{product_id}"
        r = self.s.get(url, timeout=30)
        r.raise_for_status()
        return r.json()
    
    def distinct_categories(self) -> List[str]:
        url = f"{self.base_url}/query/products/distinct/categories"
        r = self.s.get(url, timeout=30)
        r.raise_for_status()
        return r.json()

    def distinct_brands(self) -> List[str]:
        url = f"{self.base_url}/query/products/distinct/brands"
        r = self.s.get(url, timeout=30)
        r.raise_for_status()
        return r.json()
    
    def get_image_url(self, product_id: str):
        url = f"{self.base_url}/query/get_image/{product_id}"
        r = self.s.get(url, timeout=30)
        r.raise_for_status()
        return r.json()
    