from typing import Generator

from fastapi import Depends
from schema.cart_schema import Cart
from services.cart_service import CartService, cart_service_dependency


class CartViewModel:
    def __init__(self, cart_service: CartService) -> None:
        self._service = cart_service

    def get_cart(self, user_id: str) -> Cart:
        return self._service.get_cart(user_id)

    def add_to_cart(self, user_id: str, product_id: int):
        return self._service.add_to_cart(user_id, product_id)

    def remove_from_cart(self, user_id: str, product_id: int):
        return self._service.remove_from_cart(user_id, product_id)


def cart_viewmodel_dependency(
    cart_service: CartService = Depends(cart_service_dependency),
) -> Generator[CartViewModel, None, None]:

    vm = CartViewModel(cart_service)
    yield vm
