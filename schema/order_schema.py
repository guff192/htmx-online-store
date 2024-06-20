import enum
from pydantic import BaseModel
from datetime import datetime

from typing import Any

from schema import SchemaUtils
from schema.product_schema import ProductConfiguration
from schema.user_schema import UserResponse


utils = SchemaUtils()


class PaymentStatus(str, enum.Enum):
    pending = 'pending'
    success = 'success'
    failed = 'failed'


# TODO: Finish this schema and add to OrderSchema
class DeliveryAddressSchema(BaseModel):
    id: int | None
    city: str
    street: str
    house_number: str
    flat_number: str


class PaymentBase(BaseModel):
    order_id: int
    sum: int
    status: PaymentStatus = PaymentStatus.pending
    date: datetime


class PaymentSchema(PaymentBase):
    id: int

    @utils.add_shop_to_context
    def build_context(self) -> dict[str, Any]:
        return self.__dict__


class PaymentCreateSchema(PaymentBase):
    pass


class OrderProductSchema(BaseModel):
    id: int
    order_id: int
    product_id: int
    product_name: str
    count: int
    basic_price: int
    selected_configuration: ProductConfiguration

    def get_full_name(self) -> str:
        return f'{self.product_name} ({self.selected_configuration.name})'

    def get_full_price(self) -> int:
        return self.basic_price + self.selected_configuration.additional_price


class OrderBase(BaseModel):
    user_id: str
    date: datetime


class OrderSchema(OrderBase):
    id: int
    products: list[OrderProductSchema]
    sum: int
    comment: str = ''
    buyer_name: str = ''
    buyer_phone: str = ''
    delivery_address: DeliveryAddressSchema | str = ''

    @utils.add_shop_to_context
    def build_context(self) -> dict[str, Any]:
        return self.__dict__


class OrderWithPaymentSchema(OrderSchema):
    payment: PaymentSchema

    @utils.add_shop_to_context
    def build_context(self) -> dict[str, Any]:
        return self.__dict__


class OrderCreateSchema(OrderBase):
    pass


class OrderUpdateSchema(OrderCreateSchema):
    id: int
    comment: str
    buyer_name: str
    buyer_phone: str
    delivery_address: DeliveryAddressSchema | str


class UserOrderListSchema(BaseModel):
    user: UserResponse
    orders: list[OrderSchema]

    @utils.add_shop_to_context
    def build_context(self) -> dict[str, Any]:
        return self.__dict__

