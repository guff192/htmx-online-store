from fastapi import Depends
from pydantic_core import Url

from schema.product_schema import Product, ProductList, ProductPhotoPath
from services.product_service import ProductService, product_service_dependency


class ProductViewModel:
    def __init__(self, product_service: ProductService):
        self.service = product_service

    def get_all(self, offset: int) -> ProductList:
        products = self.service.get_all(offset=offset)
        if not products:
            return ProductList(products=[], offset=-5)
        # TODO: Add pagination

        product_list = ProductList(products=[], offset=offset + 10)

        for orm_product in products:
            product_dict = orm_product.__dict__
            product_name = product_dict.get('name', '')

            product_list.products.append(Product(
                id=product_dict.get('_id', 0),
                name=product_name,
                description=product_dict.get('description', ''),
                price=product_dict.get('price', 0)
            ))

        return product_list

    def get_by_id(self, product_id: int) -> Product | None:
        orm_product = self.service.get_by_id(product_id)
        if not orm_product:
            return None

        product_dict = orm_product.__dict__
        product_name = product_dict.get('name', '')
        product_photos = self.service.get_all_photos_by_name(product_name)

        return Product(
            id=product_dict.get('_id', 0),
            photos=product_photos,
            name=product_dict.get('name', ''),
            description=product_dict.get('description', ''),
            price=product_dict.get('price', 0)
        )

    def get_all_photos_by_name(self, name: str) -> list[ProductPhotoPath]:
        return self.service.get_all_photos_by_name(name)

    def get_photo_url(self, photo_path: ProductPhotoPath) -> Url:
        return self.service.get_url_by_photo_path(photo_path)

    def get_main_photo(self, product_name: str) -> ProductPhotoPath | None:
        return self.service.get_main_photo(product_name)


def product_viewmodel_dependency(
    product_service: ProductService = Depends(product_service_dependency)
):
    vm = ProductViewModel(product_service)
    yield vm

