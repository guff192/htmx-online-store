from collections.abc import Mapping
from fastapi import Depends
from exceptions.product_exceptions import ErrInvalidProduct, ErrProductNotFound

from models.product import Product
from repository.product_repository import (
    ProductRepository,
    product_repository_dependency,
)
from schema.product_schema import (
    Product as ProductSchema,
    ProductCreate,
    ProductUpdate,
    ProductUpdateResponse,
)


class ProductPhotoStorage:
    def __init__(self, credentials: Mapping[str, str]) -> None:
        raise NotImplementedError


class S3ProductPhotoStorage(ProductPhotoStorage):
    def __init__(self, s3_credentians: Mapping[str, str]) -> None:
        pass


class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.repo = product_repo

    def get_all(self) -> list[Product]:
        return self.repo.get_all()

    def get_by_id(self, product_id: int) -> Product:
        return self.repo.get_by_id(product_id)

    def get_by_name(self, name: str) -> Product:
        return self.repo.get_by_name(name)

    def update_by_name(self, product_update: ProductUpdate) -> ProductUpdateResponse:
        if not product_update.validate():
            raise ErrInvalidProduct()

        found_product = self.repo.get_by_name(product_update.name)
        if not found_product:
            raise ErrProductNotFound()

        updated_product_id = self.repo.update(
            id=found_product.__dict__['_id'],
            **product_update.model_dump()
        )
        if not updated_product_id:
            raise ErrInvalidProduct()
        return ProductUpdateResponse(count=updated_product_id)

    def search(self, name: str) -> list[Product]:
        return self.repo.search(name)

    def create(self, product_create: ProductCreate) -> ProductSchema:
        if not product_create.validate():
            raise ErrInvalidProduct()

        found_product = self.repo.get_by_name(product_create.name)
        if found_product:
            found_product = found_product.__dict__
            return ProductSchema(id=found_product['_id'], **found_product)

        created_product = self.repo.create(
            name=product_create.name,
            description=product_create.description,
            price=product_create.price,
        ).__dict__
        return ProductSchema(id=created_product['_id'], **created_product)


def product_service_dependency(
        product_repo: ProductRepository = Depends(product_repository_dependency)
):
    service = ProductService(product_repo)
    yield service

