# server/read_model/controllers.py
from typing import List, Optional
from .models import ProductReadModel, ProductRead

class ReadController:
    """
    Controller delegates to Model; here you can add light business rules if needed.
    """
    def list_products(self, include_deleted: bool=False) -> List[ProductRead]:
        return ProductReadModel.list_products(include_deleted)

    def get_product(self, product_id: str) -> Optional[ProductRead]:
        return ProductReadModel.get_product(product_id)
