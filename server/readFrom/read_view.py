"""FastAPI views (endpoints) for QUERIES only."""
from fastapi import APIRouter, HTTPException, Query
from typing import List , Optional 
from .read_controller import ReadController
from .read_model import ProductRead

router = APIRouter()
controller = ReadController()

@router.get("/products", response_model=List[ProductRead])
def list_products(q: Optional[str] = Query(None, alias="q"), category: Optional[str] = None, brand: Optional[str] = None):
    return controller.list_products(query=q, category=category, brand=brand)

@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: str):
    prod = controller.get_product(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod

@router.get("/products/distinct/categories", response_model=List[str])
def distinct_categories():
    return controller.distinct_categories()

@router.get("/products/distinct/brands", response_model=List[str])
def distinct_brands():
    return controller.distinct_brands()

@router.get("/products/{product_id}/events")
def get_product_events(product_id: str):
    return controller.product_events(product_id)

@router.get("/products_profit")
def get_products_profit():
    return controller.get_products_profit()

@router.get("/products_category_value")
def get_products_category_value():
    return controller.get_products_category_value()

@router.get("/products_total_profit_per_month")
def get_products_total_profit_per_month():
    return controller.get_products_total_profit_per_month()

@router.get("/get_image/{product_id}")
def get_product_image(product_id: str):
    return controller.get_product_image(product_id)
   