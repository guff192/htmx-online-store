from pydantic import BaseModel
from schema import SchemaUtils

from schema.product_schema import ProductList
from schema.user_schema import UserResponse


utils = SchemaUtils()


class Cart(BaseModel):
    product_list: ProductList
    user: UserResponse

    @utils.add_shop_to_context
    def build_context(self) -> dict:
        return {
            'product_list': self.product_list,
            'user': self.user,
        }

