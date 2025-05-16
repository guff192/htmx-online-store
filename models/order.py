from pydantic import BaseModel, NonNegativeInt

from models.payment import Payment
from models.product_configuration import ProductConfiguration
from models.user import UserId


class OrderProduct:
    id: int
    product_id: int
    quantity: NonNegativeInt
    
    name: str
    price: int
    selected_configurations: list[ProductConfiguration]


class DeliveryRegion(BaseModel):
    code: int
    name: str


class DeliveryCity(BaseModel):
    code: int
    name: str


class DeliveryAddress(BaseModel):
    delivery_name: str
    delivery_phone: str

    region: DeliveryRegion
    city: DeliveryCity
    address_str: str


class Order(BaseModel):
    id: int
    user_id: UserId

    products: list[OrderProduct]
    
    address: DeliveryAddress
    track_number: str

    payment: Payment | None
