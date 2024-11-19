from typing import Any
from pydantic import BaseModel
from schema import SchemaUtils

from schema.product_schema import Product
from schema.user_schema import UserResponse


utils = SchemaUtils()


class ProductInCart(Product):
    count: int 


class Cart(BaseModel):
    user: UserResponse
    product_list: list[ProductInCart]

    @utils.add_debug_info_to_context
    @utils.add_shop_to_context
    def build_context(self) -> dict:
        return {
            'product_list': self.product_list,
            'user': self.user,
        }

    def total_count(self) -> int:
        return sum([p.count for p in self.product_list])


class CookieCartProduct(BaseModel):
    product_id: int
    configuration_id: int
    count: int

    def build_context(self) -> dict[str, Any]:
        return {'product': self}


class CartInCookie(BaseModel):
    product_list: list[CookieCartProduct]

    @utils.add_shop_to_context
    def build_context(self) -> dict[str, Any]:
        return self.__dict__

    def cookie_str(self) -> str:
        cookie_cart_str = '{"product_list": ['
        products_count = len(self.product_list)
        for i, cart_product in enumerate(self.product_list):
            cookie_cart_str += f'{{"product_id": {cart_product.product_id}, '
            cookie_cart_str += f'"configuration_id": {cart_product.configuration_id}, '
            cookie_cart_str += f'"count": {cart_product.count}}}'
            cookie_cart_str += ',' if i != products_count - 1 else ''
        cookie_cart_str += ']}'

        return cookie_cart_str

    def total_count(self) -> int:
        return sum([p.count for p in self.product_list])


class ProductAddToCartRequest(BaseModel):
    product_id: int
    configuration_id: int

