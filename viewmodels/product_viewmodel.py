from fastapi import Depends

from schema.product_schema import Product, ProductList
from services.product_service import ProductService, product_service_dependency


class ProductViewModel:
    def __init__(self, product_service: ProductService):
        self.service = product_service

    def get_all(self) -> ProductList:
        products = self.service.get_all()
        # TODO: Add pagination

        product_list = ProductList(products=[])

        for orm_product in products:
            product_dict = orm_product.__dict__
            _id = product_dict.get('_id', 0)
            name: str = product_dict.get('name', '')
            description: str = product_dict.get('description', '')
            price = product_dict.get('price', 0)

            product_list.products.append(Product(
                id=_id,
                name=name,
                description=description,
                price=price
            ))
        return product_list

    def get_by_id(self, product_id: int) -> Product | None:
        orm_product = self.service.get_by_id(product_id)
        if not orm_product:
            return None

        product_dict = orm_product.__dict__
        _id = product_dict.get('_id', 0)
        name = str(product_dict.get('name', ''))
        description = str(product_dict.get('description', ''))
        price = product_dict.get('price', 0) 

        return Product(
            id=_id,
            name=name,
            description=description,
            price=price
        )


def product_viewmodel_dependency(product_service: ProductService = Depends(product_service_dependency)):
    vm = ProductViewModel(product_service)
    yield vm

