from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import reconstructor
from app.config import Settings
from schema.order_schema import CitySchema, OrderProductSchema, RegionSchema
from services.delivery_service import DeliveryService, delivery_service_dependency


class DeliveryViewModel:
    def __init__(self, service: DeliveryService):
        self._service = service

    def get_regions(self) -> list[RegionSchema]:
        return self._service.get_regions()

    def get_cities(self, region_code: int) -> list[CitySchema]:
        return self._service.get_cities(region_code)

    def get_shipping_cost(self, city_code: int, products_count: int) -> int:
        return self._service.get_shipping_cost(city_code, products_count)

    def get_cdek_order_number(self, order_id: int) -> str:
        return self._service.get_cdek_order_number(order_id)

    def create_delivery_order(
        self,
        order_id: int,
        receiver_city_id: int,
        receiver_address: str,
        recipient_name: str,
        recipient_phone: str,
        recipient_email: str,
        products: list[OrderProductSchema],
    ):
        return self._service.create_delivery_order(
            order_id=order_id,
            receiver_city_id=receiver_city_id,
            receiver_address=receiver_address,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            recipient_email=recipient_email,
            products=products,
        )


def delivery_viewmodel_dependency(
    service: DeliveryService = Depends(delivery_service_dependency),
) -> Generator[DeliveryViewModel, None, None]:
    vm = DeliveryViewModel(service)
    yield vm

