"""FastAPI views (endpoints) for QUERIES only."""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from .controllers import ReadController
from .models import ProductRead

router = APIRouter()
controller = ReadController()

@router.get("/products", response_model=List[ProductRead])
def list_products(include_deleted: bool = Query(False)):
    return controller.list_products(include_deleted)

@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: str):
    prod = controller.get_product(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod
