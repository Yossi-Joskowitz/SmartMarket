from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import os
import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


@dataclass
class ReadProduct:
    product_id: str
    name: str
    price: float
    quantity: int
    is_deleted: bool
    is_on_promotion: bool = False
    brand: Optional[str] = None
    category: Optional[str] = None

    @staticmethod
    def from_json(j: Dict[str, Any]) -> "ReadProduct":
        return ReadProduct(
            product_id=j.get("product_id", ""),
            name=j.get("name", ""),
            price=float(j.get("price", 0.0)),
            quantity=int(j.get("quantity", 0)),
            is_deleted=bool(j.get("is_deleted", False)),
            is_on_promotion=bool(j.get("is_on_promotion", j.get("IsOnPromotion", False))),
            brand=j.get("brand") or j.get("Brand"),
            category=j.get("category") or j.get("Category"),
        )


class InventoryModel:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or BASE_URL
        self.s = requests.Session()

    # ---------- Queries ----------
    def list_products(
        self,
        include_deleted: bool = False,
        *,
        query: Optional[str] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: Optional[str] = None,  
        sort_dir: Optional[str] = None,  
    ) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/query/products"
        params: Dict[str, Any] = {"include_deleted": str(include_deleted).lower()}
        if query:    params["q"] = query            # ← שם הפרמטר ב־API
        if category: params["category"] = category
        if brand:    params["brand"] = brand
        if limit is not None:   params["limit"] = str(limit)
        if offset is not None:  params["offset"] = str(offset)
        if sort_by:  params["sort_by"] = sort_by
        if sort_dir: params["sort_dir"] = sort_dir

        r = self.s.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def get_product(self, product_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/query/products/{product_id}"
        r = self.s.get(url, timeout=30)
        r.raise_for_status()
        return r.json()

    # ---------- Commands ----------
    def create_product(
        self,
        product_id: str,
        name: str,
        price: float,
        quantity: int,
        *,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        is_on_promotion: Optional[bool | int] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/command/product/create"
        payload: Dict[str, Any] = {
            "product_id": product_id,
            "name": name,
            "price": float(price),
            "quantity": int(quantity),
        }
        if brand is not None:
            payload["brand"] = brand
        if category is not None:
            payload["category"] = category
        if is_on_promotion is not None:
            payload["is_on_promotion"] = 1 if int(is_on_promotion) else 0

        r = self.s.post(url, json=payload, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(r.text)
        try:
            return r.json()
        except Exception:
            return {}

    def update_product(
        self,
        product_id: str,
        *,
        name: Optional[str] = None,
        price: Optional[float] = None,
        quantity: Optional[int] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        is_on_promotion: Optional[bool | int] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/command/product/{product_id}/update"
        payload: Dict[str, Any] = {}

        if name is not None:
            payload["name"] = name
        if price is not None:
            payload["price"] = float(price)
        if quantity is not None:
            payload["quantity"] = int(quantity)
        if brand is not None:
            payload["brand"] = brand
        if category is not None:
            payload["category"] = category
        if is_on_promotion is not None:
            payload["is_on_promotion"] = 1 if int(is_on_promotion) else 0

        r = self.s.put(url, json=payload, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(r.text)
        try:
            return r.json()
        except Exception:
            return {}

    def delete_product(self, product_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/command/product/{product_id}/delete"
        r = self.s.delete(url, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(r.text)
        try:
            return r.json()
        except Exception:
            return {}
        
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

