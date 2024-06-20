from pydantic import BaseModel
from schema import SchemaUtils

from schema.product_schema import ProductInCart
from schema.user_schema import UserResponse


utils = SchemaUtils()


class Cart(BaseModel):
    product_list: list[ProductInCart]
    user: UserResponse

    @utils.add_shop_to_context
    def build_context(self) -> dict:
        return {
            'product_list': self.product_list,
            'user': self.user,
        }


class ProductAddToCartRequest(BaseModel):
    product_id: int
    configuration_id: int

