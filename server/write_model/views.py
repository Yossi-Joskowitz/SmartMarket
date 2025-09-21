"""FastAPI views (endpoints) for COMMANDS only."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from .controllers import WriteController

router = APIRouter()
controller = WriteController()

class CreateProductDto(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int
    brand: Optional[str] = None
    category: Optional[str] = None
    is_on_promotion: int = 0

class UpdateProductDto(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    is_on_promotion: Optional[int] = None

@router.post("/product/create")
def create_product(dto: CreateProductDto):
    try:
        return controller.create_product(
        dto.product_id,
        dto.name,
        float(dto.price),
        int(dto.quantity),
        dto.brand,
        dto.category,
        int(dto.is_on_promotion),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/product/{product_id}/update")
def update_product(product_id: str, dto: UpdateProductDto):
    try:
        return controller.update_product(
        product_id,
        dto.name,
        float(dto.price) if dto.price is not None else None,
        int(dto.quantity) if dto.quantity is not None else None,
        dto.brand,
        dto.category,
        int(dto.is_on_promotion) if dto.is_on_promotion is not None else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/product/{product_id}/delete")
def delete_product(product_id: str):
    try:
        return controller.delete_product(product_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
