from typing import Generator

from fastapi import Depends
from schema.cart_schema import CartInCookie
from schema.order_schema import (
    OrderCreateSchema, OrderInCookie, OrderSchema, OrderUpdateSchema,
    UserOrderListSchema
)
from schema.user_schema import UserCreate, UserResponse
from services.order_service import OrderService, order_service_dependency


class OrderViewModel:
    def __init__(self, service: OrderService):
        self._service = service
    
    def get_by_id(self, order_id: int, user_id: str) -> OrderSchema:
        return self._service.get_by_id(order_id, user_id)

    def list_user_orders(self, user_id: str) -> UserOrderListSchema:
        return self._service.list_user_orders(user_id)

    def create_from_cookie_cart(self, cart: CartInCookie) -> OrderInCookie:
        return self._service.create_from_cookie_cart(cart)

    def create_order(self, order: OrderCreateSchema) -> OrderSchema:
        return self._service.create_from_cart(order.user_id)

    def create_user_for_order(self, user: UserCreate) -> UserResponse:
        return self._service.create_user_for_order(user)

    def update_order(self, order: OrderUpdateSchema) -> OrderSchema:
        return self._service.update_order(order)

    def remove_order(self, order_id: int, user_id: str) -> None:
        self._service.remove_order(order_id, user_id)


def order_viewmodel_dependency(
    service: OrderService = Depends(order_service_dependency),
) -> Generator[OrderViewModel, None, None]:
    vm = OrderViewModel(service)
    yield vm

