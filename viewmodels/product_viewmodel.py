from typing import Generator

from fastapi import Depends
from pydantic_core import Url

from schema.product_schema import (
    Product,
    ProductList,
    ProductPhotoPath,
    ProductPhotoSize,
)
from schema.user_schema import LoggedUser
from services.product_service import ProductService, product_service_dependency


class ProductViewModel:
    def __init__(
        self,
        product_service: ProductService,
    ) -> None:
        self._service = product_service

    def get_all(
        self,
        offset: int,
        user: LoggedUser | None = None
    ) -> ProductList:
        return self._service.get_all(offset=offset, user=user)

    def get_newcomers(
        self,
        offset: int,
    ) -> ProductList:
        return self._service.get_newcomers(offset=offset)

    def get_by_id(self, product_id: int) -> Product:
        return self._service.get_by_id(product_id)

    def get_all_photos_by_name(
        self, name: str, size: ProductPhotoSize = ProductPhotoSize.thumbs
    ) -> list[ProductPhotoPath]:
        return self._service.get_all_photos_by_name(name, size)

    def get_photo_url(self, photo_path: ProductPhotoPath) -> Url:
        return self._service.get_url_by_photo_path(photo_path)

    def get_main_photo(
        # TODO: change size to enum
        self,
        product_name: str,
        size: ProductPhotoSize = ProductPhotoSize.small,
    ) -> ProductPhotoPath | None:
        return self._service.get_main_photo(product_name, size)


def product_viewmodel_dependency(
    product_service: ProductService = Depends(product_service_dependency),
) -> Generator[ProductViewModel, None, None]:
    vm = ProductViewModel(product_service)
    yield vm

