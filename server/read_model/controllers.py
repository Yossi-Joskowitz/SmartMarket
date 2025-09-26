# server/read_model/controllers.py
from typing import List, Optional
from .models import ProductReadModel, ProductRead

class ReadController:
    """
    Controller delegates to Model; here you can add light business rules if needed.
    """
    def list_products(
        self,
        *,
        query: Optional[str],
        category: Optional[str],
        brand: Optional[str],
        include_deleted: bool,
        limit: int,
        offset: int,
        sort_by: str,
        sort_dir: str,
    ) -> List[ProductRead]:
        return ProductReadModel.list_products(
            query=query,            
            category=category,
            brand=brand,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )


    def get_product(self, product_id: str) -> Optional[ProductRead]:
        return ProductReadModel.get_product(product_id)
    
    def distinct_categories(self) -> List[str]:
        return ProductReadModel.distinct_categories()

    def distinct_brands(self) -> List[str]:
        return ProductReadModel.distinct_brands()
