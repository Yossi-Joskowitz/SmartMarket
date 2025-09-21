from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import os, requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")

@dataclass
class ReadProduct:
    product_id: str
    name: str
    price: float
    quantity: int
    is_deleted: bool
    is_on_promotion: bool = False
    brand: str | None = None
    category: str | None = None

    @staticmethod
    def from_json(j):
        return ReadProduct(
            product_id=j.get("product_id",""),
            name=j.get("name",""),
            price=float(j.get("price",0.0)),
            quantity=int(j.get("quantity",0)),
            is_deleted=bool(j.get("is_deleted", False)),
            is_on_promotion=bool(j.get("is_on_promotion", j.get("IsOnPromotion", False))),
            brand=j.get("brand") or j.get("Brand"),
            category=j.get("category") or j.get("Category"),
        )


class ApiService:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or BASE_URL
        self.s = requests.Session()

    # Queries
    def list_products(self, include_deleted: bool=False) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/query/products"
        params = {"include_deleted": str(include_deleted).lower()}
        r = self.s.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def get_product(self, product_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/query/products/{product_id}"
        r = self.s.get(url, timeout=30)
        r.raise_for_status()
        return r.json()

    # Commands
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
        # שדות אופציונליים – נכניס רק אם סופקו
        if brand is not None: payload["brand"] = brand
        if category is not None: payload["category"] = category
        if is_on_promotion is not None:
            payload["is_on_promotion"] = 1 if int(is_on_promotion) else 0


        r = self.s.post(url, json=payload, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(r.text)
        # אם השרת מחזיר 204/גוף ריק זה יפיל json(); עטוף בגיבוי אם צריך
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

        # הוסף לשיוך רק שדות שסופקו (לא None)
        if name is not None: payload["name"] = name
        if price is not None: payload["price"] = float(price)
        if quantity is not None: payload["quantity"] = int(quantity)
        if brand is not None: payload["brand"] = brand
        if category is not None: payload["category"] = category
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
        return r.json()
