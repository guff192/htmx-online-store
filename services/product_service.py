from fastapi import Depends

from repository.product_repository import ProductRepository, product_repository_dependency
from models.product import Product


class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.repo = product_repo

    def get_all(self) -> list[Product]:
        return self.repo.get_all()

    def get_by_id(self, product_id: int) -> Product:
        return self.repo.get_by_id(product_id)


def product_service_dependency(product_repo: ProductRepository = Depends(product_repository_dependency)):
    service = ProductService(product_repo)
    yield service

