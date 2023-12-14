import time

from fastapi import Depends
from loguru import logger
from pydantic_core import Url

from exceptions.product_exceptions import ErrInvalidProduct, ErrProductNotFound
from models.product import Product
from repository.product_repository import (
    ProductRepository,
    product_repository_dependency,
)
from schema.product_schema import (
    Product as ProductSchema,
    ProductCreate,
    ProductPhotoPath,
    ProductPhotoSize,
    ProductUpdate,
    ProductUpdateResponse,
)
from storage.photo_storage import ProductPhotoStorage, product_photo_storage_dependency


class ProductService:
    def __init__(
            self,
            product_repo: ProductRepository,
            photo_storage: ProductPhotoStorage
    ):
        self.repo = product_repo
        self.photo_storage = photo_storage

    def get_all(self, offset: int) -> list[Product]:
        if offset < 0:
            raise ErrProductNotFound()
        return self.repo.get_all(offset=offset)

    def get_by_id(self, product_id: int) -> Product:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise ErrProductNotFound()

        return product

    def get_by_name(self, name: str) -> Product:
        return self.repo.get_by_name(name)

    def get_url_by_photo_path(
        self,
        photo_path: ProductPhotoPath,
    ) -> Url:
        return self.photo_storage.get_url(photo_path)

    def get_main_photo(
            self,
            product_name: str,
            size: ProductPhotoSize = ProductPhotoSize.small
    ) -> ProductPhotoPath | None:
        start = time.time()
        result = self.photo_storage.get_main_photo_by_name(product_name, size)
        logger.debug(f'Get main photo time: {time.time() - start}')

        return result

    def get_all_photos_by_name(
            self, name: str, size: ProductPhotoSize = ProductPhotoSize.thumbs
    ) -> list[ProductPhotoPath]:
        return self.photo_storage.get_all_by_name(name, size)

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
        product_repo: ProductRepository = Depends(product_repository_dependency),
        photo_storage: ProductPhotoStorage = Depends(product_photo_storage_dependency),
):
    service = ProductService(product_repo, photo_storage)
    yield service

