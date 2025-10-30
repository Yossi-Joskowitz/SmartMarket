# server/read_model/controllers.py
from typing import List, Optional
from .read_model import ReadModel, ProductRead

class ReadController:
    """
    Controller delegates to Model; here you can add light business rules if needed.
    """
    def list_products(self,*,query: Optional[str],category: Optional[str],brand: Optional[str],) -> List[ProductRead]:
        return ReadModel.list_products(query=query, category=category, brand=brand)

    def get_product(self, product_id: str) -> Optional[ProductRead]:
        return ReadModel.get_product(product_id)
    
    def distinct_categories(self) -> List[str]:
        return ReadModel.distinct_categories()

    def distinct_brands(self) -> List[str]:
        return ReadModel.distinct_brands()

    def product_events(self, product_id: str):
        return ReadModel.product_events(product_id)
    
    def get_products_profit(self):
        return ReadModel.get_products_profit()
    
    def get_products_category_value(self):
        return ReadModel.get_products_category_value()
    
    def get_products_total_profit_per_month(self):
        return ReadModel.get_products_total_profit_per_month()
    
    def get_product_image(self, product_id: str):
        return ReadModel.get_product_image(product_id)