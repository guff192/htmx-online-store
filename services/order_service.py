from datetime import datetime
from fastapi import Depends
from typing import Generator

from loguru import logger

from exceptions.order_exceptions import ErrOrderNotFound, ErrUserOrdersNotFound
from models.order import Order, OrderProduct
from repository.cart_repository import CartRepository, cart_repository_dependency
from repository.configuration_repository import ConfigurationRepository, configuration_repository_dependency
from repository.order_repository import (
    OrderRepository, order_repository_dependency
)
from repository.product_repository import ProductRepository, product_repository_dependency
from schema.order_schema import OrderProductSchema, OrderSchema, OrderUpdateSchema, OrderWithPaymentSchema, PaymentSchema, PaymentStatus, UserOrderListSchema
from schema.product_schema import ProductConfiguration as ProductConfigurationSchema
from services.user_service import UserService, user_service_dependency


class OrderService:
    def __init__(self, repo: OrderRepository,
                 cart_repo: CartRepository,
                 config_repo: ConfigurationRepository,
                 product_repo: ProductRepository,
                 user_service: UserService) -> None:
        self._repo = repo
        self._cart_repo = cart_repo
        self._config_repo = config_repo
        self._product_repo = product_repo
        self._user_service = user_service

    def _order_model_to_schema(self, order_model: Order) -> OrderSchema | OrderWithPaymentSchema:
        # getting data from model
        order_model_dict = order_model.__dict__
        order_id = order_model_dict.get('id', 0)
        user_id = str(order_model_dict.get('user_id', ''))
        order_date = order_model_dict.get('date', datetime.now())
        order_comment = order_model_dict.get('comment', '')
        order_buyer_name = order_model_dict.get('buyer_name', '')
        order_buyer_phone = order_model_dict.get('buyer_phone', '')
        order_address = order_model_dict.get('delivery_address', '')

        # creating order products schema
        order_products_model: list[OrderProduct] = self.get_order_products(order_model.id)
        order_products_schema: list[OrderProductSchema] = []
        sum = 0
        for order_product in order_products_model:
            op_dict = order_product.__dict__
            id_ = op_dict.get('id', 0)
            order_id = op_dict.get('order_id', 0)
            product_id = op_dict.get('product_id', 0)

            product = self._product_repo.get_by_id(product_id)
            product_name = product.__dict__.get('name', '')
            product_basic_price = product.__dict__.get('price', 0)

            count = op_dict.get('count', 0)
            selected_config_dict = order_product.selected_configuration.__dict__
            selected_configuration = ProductConfigurationSchema(
                id=selected_config_dict['id'],
                name=selected_config_dict['name'],
                additional_price=selected_config_dict['additional_price'],
            )
            
            order_product_schema = OrderProductSchema(
                id=id_,
                order_id=order_id,
                product_id=product_id,
                product_name=product_name,
                count=count,
                basic_price=product_basic_price,
                selected_configuration=selected_configuration
            )

            order_products_schema.append(order_product_schema)
            sum += (product_basic_price + selected_configuration.additional_price) * count

        order_payment = order_model.payment
        if order_payment is not None:
            order_payment_dict = order_payment.__dict__
            payment_schema = PaymentSchema(
                id=order_payment_dict.get('id', 0),
                order_id=order_id,
                status=PaymentStatus(order_payment_dict.get('status', '')),
                sum=sum,
                date=order_payment_dict.get('date', datetime.now()),
            )

            order_schema = OrderWithPaymentSchema(
                id=order_id,
                user_id=user_id,
                date=order_date,
                products=order_products_schema,
                sum=sum,
                comment=order_comment,
                buyer_name=order_buyer_name,
                buyer_phone=order_buyer_phone,
                delivery_address=order_address,
                payment=payment_schema
            )
        else:
            order_schema = OrderSchema(
                id=order_id,
                user_id=user_id,
                date=order_date,
                products=order_products_schema,
                sum=sum,
                comment=order_comment,
                buyer_name=order_buyer_name,
                buyer_phone=order_buyer_phone,
                delivery_address=order_address
            )

        return order_schema

    def get_order_sum(self, order_id: int) -> int:
        order_model = self._repo.get_by_id(order_id)
        if not order_model:
            raise ErrOrderNotFound(order_id)

        order_products = self.get_order_products(order_id)
        sum: int = 0
        for order_product in order_products:
            product_price: int = order_product.product.__dict__.get('price', 0)
            additional_price: int = order_product.selected_configuration.__dict__.get('additional_price', 0)
            sum += (product_price + additional_price) * order_product.__dict__.get('count', 0)

        return sum

    def get_by_id(self, order_id: int, user_id: str) -> OrderSchema:
        order_model = self._repo.get_by_id(order_id)
        if not order_model:
            logger.debug(f'{order_id = }')
            raise ErrOrderNotFound(order_id)

        order_schema = self._order_model_to_schema(order_model)
        if not order_schema.user_id == user_id:
            raise ErrOrderNotFound(order_id)


        return order_schema

    def list_user_orders(self, user_id: str) -> UserOrderListSchema:
        user_model = self._user_service.get_by_id(user_id)
        if not user_model:
            raise ErrUserOrdersNotFound()


        user_response_schema = (self._user_service.
                                user_model_to_userresponse_schema(user_model))
        user_orders_model = self._repo.list_user_orders(user_id)

        user_orders_schema = UserOrderListSchema(
            user=user_response_schema,
            orders=[self._order_model_to_schema(order) for order in user_orders_model]
        )

        return user_orders_schema

    def get_order_products(self, order_id) -> list[OrderProduct]:
        return self._repo.get_order_products(order_id)

    def create_from_cart(self, user_id: str) -> OrderSchema:
        # creating order
        user_products = self._cart_repo.get_user_products(user_id)
        order_model = self._repo.create(user_id, user_products)

        return self._order_model_to_schema(order_model)

    def update_order(self, order_update: OrderUpdateSchema) -> OrderSchema:
        if not isinstance(order_update.delivery_address, str):
            order_update.delivery_address = (
                order_update.delivery_address.city
                + order_update.delivery_address.street
                + order_update.delivery_address.house_number
                + order_update.delivery_address.flat_number
            )

        order_model = self._repo.update(order_update.id, order_update.user_id,
                                        order_update.comment,
                                        order_update.buyer_name,
                                        order_update.delivery_address,
                                        order_update.buyer_phone)

        return self._order_model_to_schema(order_model)

    def remove_order(self, order_id: int, user_id: str) -> None:
        self._repo.remove(order_id, user_id)



def order_service_dependency(
    repo: OrderRepository = Depends(order_repository_dependency),
    cart_repo: CartRepository = Depends(cart_repository_dependency),
    config_repo: ConfigurationRepository = Depends(
        configuration_repository_dependency
    ),
    product_repo: ProductRepository = Depends(product_repository_dependency),
    user_service: UserService = Depends(user_service_dependency)
) -> Generator[OrderService, None, None]:

    service = OrderService(repo, cart_repo, config_repo, product_repo, user_service)
    yield service

