
# views.py
# Minimal "usage example" (not a GUI). Acts as a stub demonstrating the controller API.
# Run this after setting SMARTMARKET_ODBC env var to your pyodbc SQL Server connection string.
from __future__ import annotations
from typing import Dict, Any
from .write_model import Product
from .write_controller import writeController
from fastapi import APIRouter, HTTPException
from typing import Optional
from fastapi import Body

router = APIRouter()
controller = writeController()

@router.post("/product/create")
def create_product(dto: Product):
    try:
        controller.create_product(dto)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/product/{product_id}/update")
def update_product(product_id: str, fields: Dict[str, Any]):
    try:
        controller.update_product(product_id, fields)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete("/product/{product_id}/delete")
def delete_product(product_id: str):
    try:
        controller.delete_product(product_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/product/{product_id}/sale")
def sale_product(product_id: str, quantity: int, sale_unit_price: float, sale_unit_cost: float):
    try:
        controller.sale(product_id, quantity, sale_unit_price, sale_unit_cost)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/product/{product_id}/add_note")
def add_note(product_id: str, note: str):
    try:
        controller.add_note(product_id, note)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/product/{product_id}/set_promotion")
def set_promotion(product_id: str, is_on_promotion: bool, promotion_discount_percent: float):
    try:
        controller.set_promotion(product_id, is_on_promotion, promotion_discount_percent)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/product/{product_id}/purchase")
def purchase_product(product_id: str, quantity: int, purchase_unit_cost: float):
    try:
        controller.purchase(product_id, quantity, purchase_unit_cost)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/product/{product_id}/change_price")
def change_price(product_id: str, current_price: Optional[float] = None, cost_price: Optional[float] = None):
    try:
        controller.change_price(product_id, current_price=current_price, cost_price=cost_price)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/product/{product_id}/UploadImage")
def upload_image(product_id: str, image_url: str = Body(..., embed=True)):
    try:
        controller.upload_image(product_id, image_url)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))