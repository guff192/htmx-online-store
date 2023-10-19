from fastapi import Depends

from repository.product_repository import ProductRepository, get_product_repository
from models.product import Product


class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.repo = product_repo

    def get_all(self) -> list[Product]:
        return self.repo.get_all()


def get_product_service(product_repo: ProductRepository = Depends(get_product_repository)):
    service = ProductService(product_repo)
    yield service

