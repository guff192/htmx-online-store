from uuid import UUID
from pydantic import BaseModel, NonNegativeInt

from models.product_configuration import ProductConfiguration


class CartProduct(BaseModel):
    id: int
    product_id: int
    quantity: NonNegativeInt

    name: str
    price: int
    selected_configurations: list[ProductConfiguration]
    

class Cart(BaseModel):
    user_id: UUID
    products: list[CartProduct]
