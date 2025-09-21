"""FastAPI views (endpoints) for COMMANDS only."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from .controllers import WriteController

router = APIRouter()
controller = WriteController()

class CreateProductDto(BaseModel):
    product_id: str = Field(..., description="Aggregate ID, e.g. SKU or UUID")
    name: str
    price: float
    quantity: int

class UpdateProductDto(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None

@router.post("/product/create")
def create_product(dto: CreateProductDto):
    try:
        return controller.create_product(dto.product_id, dto.name, dto.price, dto.quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/product/{product_id}/update")
def update_product(product_id: str, dto: UpdateProductDto):
    try:
        return controller.update_product(product_id, dto.name, dto.price, dto.quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/product/{product_id}/delete")
def delete_product(product_id: str):
    try:
        return controller.delete_product(product_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
