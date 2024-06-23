from datetime import datetime
import enum
from hashlib import sha256
from typing import Any, OrderedDict

from loguru import logger
from pydantic import BaseModel, Field

from app.config import Settings
from schema import SchemaUtils
from schema.product_schema import ProductConfiguration
from schema.user_schema import UserResponse


settings = Settings()
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


class TinkoffPaymentStatus(str, enum.Enum):
    AUTHORIZED = 'AUTHORIZED'
    CONFIRMED = 'CONFIRMED'
    PARTIAL_REVERSED = 'PARTIAL_REVERSED'
    REVERSED = 'REVERSED'
    PARTIAL_REFUNDED = 'PARTIAL_REFUNDED'
    REFUNDED = 'REFUNDED'
    REJECTED = 'REJECTED'


class TinkoffWebhookRequest(BaseModel):
    terminal_key: str = Field(..., alias='TerminalKey')
    order_id: str = Field(..., alias='OrderId')
    success: bool = Field(..., alias='Success')
    status: TinkoffPaymentStatus = Field(..., alias='Status')
    payment_id: int = Field(..., alias='PaymentId')
    error_code: str = Field(..., alias='ErrorCode')
    amount: int = Field(..., alias='Amount')
    card_id: int = Field(..., alias='CardId')
    pan: str = Field(..., alias='Pan')
    exp_date: str = Field(..., alias='ExpDate')
    token: str = Field(..., alias='Token')

    def is_valid(self) -> bool:
        token_creation_data = self.model_dump(exclude={'token'})
        token_creation_data.update(password=settings.tinkoff_terminal_password)
        sorted_keys = sorted(list(token_creation_data.keys()))
        
        bytes_to_hash = b''
        for key in sorted_keys:
            value = token_creation_data[key]
            if value in (True, False):
                str_value = str(value).lower()
            elif key == 'status':
                str_value = value.value
            else:
                str_value = str(value)
            
            bytes_to_hash += bytes(str_value, encoding='utf-8')

        hash = sha256(bytes_to_hash).hexdigest()

        return hash == self.token


class TinkoffWebhookTokenCreationData(TinkoffWebhookRequest):
    password: str = Field(..., alias='Password')


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

