from typing import Generator

from fastapi import Depends
from schema.cart_schema import Cart, CartInCookie
from schema.product_schema import ProductInCart
from services.cart_service import CartService, cart_service_dependency


class CartViewModel:
    def __init__(self, cart_service: CartService) -> None:
        self._service = cart_service

    def from_cookie(self, cookie_cart: CartInCookie) -> list[ProductInCart]:
        return self._service.from_cookie_schema(cookie_cart)

    def get_cart(self, user_id: str) -> Cart:
        return self._service.get_cart(user_id)

    def get_product_in_cart(self, user_id: str, product_id: int) -> ProductInCart:
        return self._service.get_product_in_cart(user_id, product_id)

    def add_to_cart(
        self, user_id: str, product_id: int, configuration_id: int
    ) -> ProductInCart:
        return self._service.add_to_cart(user_id, product_id, configuration_id)

    def remove_from_cart(self, user_id: str,
                         configuration_id: int,
                         product_id: int) -> ProductInCart:
        return self._service.remove_from_cart(user_id,
                                              configuration_id, product_id)


def cart_viewmodel_dependency(
    cart_service: CartService = Depends(cart_service_dependency),
) -> Generator[CartViewModel, None, None]:
    vm = CartViewModel(cart_service)
    yield vm
