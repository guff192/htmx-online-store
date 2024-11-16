from typing import Generator

from fastapi import Depends
from pydantic_core import Url

from schema.product_schema import (
    Product,
    ProductList,
    ProductPhotoPath,
    ProductPhotoSize,
    ProductConfiguration,
    ProductPrices
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
        query: str,
        offset: int,
        user: LoggedUser | None = None,
        price_from: int = 0, price_to: int = 150000,
        ram: list[int] = [], ssd: list[int] = [], cpu: list[str] = [],
        resolution: list[str] = [], touchscreen: list[bool] = [],
        graphics: list[bool] = [],
    ) -> ProductList:
        return self._service.get_all(
            query=query,
            offset=offset, user=user,
            price_from=price_from, price_to=price_to,
            ram=ram, ssd=ssd, cpu=cpu, resolution=resolution,
            touchscreen=touchscreen, graphics=graphics
        )

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
        self,
        product_name: str,
        size: ProductPhotoSize = ProductPhotoSize.small,
    ) -> ProductPhotoPath | None:
        return self._service.get_main_photo(product_name, size)

    def get_configurations_for_product(
        self,
        product_id: int
    ) -> list[ProductConfiguration]:
        return self._service.get_configurations_for_product(product_id)

    def get_product_prices(
        self,
        product_id: int,
        configuration_id: int
    ) -> ProductPrices:
        return self._service.get_product_prices(product_id, configuration_id)

    def search(
        self,
        query: str,
        offset: int
    ) -> ProductList:
        return self._service.search(query, offset)


def product_viewmodel_dependency(
    product_service: ProductService = Depends(product_service_dependency),
) -> Generator[ProductViewModel, None, None]:
    vm = ProductViewModel(product_service)
    yield vm

