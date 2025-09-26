"""FastAPI views (endpoints) for QUERIES only."""
from fastapi import APIRouter, HTTPException, Query
from typing import List , Optional
from .controllers import ReadController
from .models import ProductRead

router = APIRouter()
controller = ReadController()

@router.get("/products", response_model=List[ProductRead])
def list_products(
    q: Optional[str] = Query(None, alias="q"),
    category: Optional[str] = None,
    brand: Optional[str] = None,
    include_deleted: bool = False,
    limit: int = 200,
    offset: int = 0,
    sort_by: str = "name",
    sort_dir: str = "asc",
):
    return controller.list_products(
        query=q,                    
        category=category,
        brand=brand,
        include_deleted=include_deleted,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )

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
