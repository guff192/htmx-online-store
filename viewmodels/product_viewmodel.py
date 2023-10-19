from fastapi import Depends

from schema.product_schema import Product, ProductList
from services.product_service import ProductService, get_product_service


class ProductViewModel:
    def __init__(self, product_service: ProductService):
        self.service = product_service

    def get_all(self) -> ProductList:
        products = self.service.get_all()

        product_list = ProductList(products=[])

        for orm_product in products:
            product_dict = orm_product.__dict__
            product_list.products.append(Product(
                id=product_dict.get('id', 0),
                name=str(product_dict.get('name', '')),
                description=str(product_dict.get('description', '')),
                price=product_dict.get('price', 0),
            ))

        return product_list


def get_product_viewmodel(product_service: ProductService = Depends(get_product_service)):
    vm = ProductViewModel(product_service)
    yield vm
