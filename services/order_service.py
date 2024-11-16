from datetime import datetime, timezone
from fastapi import Depends
from typing import Generator

from loguru import logger

from exceptions.order_exceptions import ErrOrderNotFound, ErrUserOrdersNotFound
from models.order import Order, OrderProduct
from repository.cart_repository import CartRepository, cart_repository_dependency
from repository.configuration_repository import (
    ConfigurationRepository, configuration_repository_dependency
)
from repository.order_repository import (
    OrderRepository, order_repository_dependency
)
from repository.product_repository import (
    ProductRepository, product_repository_dependency
)
from schema.cart_schema import CartInCookie
from schema.order_schema import (
    CitySchema, CookieOrderProduct, DeliveryAddressSchema, OrderInCookie, OrderProductSchema, OrderSchema, OrderUpdateSchema, OrderWithPaymentSchema,
    PaymentSchema, PaymentStatus, RegionSchema, UserOrderListSchema
)
from schema.product_schema import ProductConfiguration as ProductConfigurationSchema
from schema.user_schema import UserCreate, UserResponse
from services.delivery_service import DeliveryService, delivery_service_dependency
from services.user_service import UserService, user_service_dependency


class OrderService:
    def __init__(self, repo: OrderRepository,
                 cart_repo: CartRepository,
                 config_repo: ConfigurationRepository,
                 product_repo: ProductRepository,
                 user_service: UserService,
                 delivery_service: DeliveryService) -> None:
        self._repo = repo
        self._cart_repo = cart_repo
        self._config_repo = config_repo
        self._product_repo = product_repo
        self._user_service = user_service
        self._delivery_service = delivery_service

    def _order_model_to_schema(self, order_model: Order) -> OrderSchema | OrderWithPaymentSchema:
        # getting data from model
        order_model_dict = order_model.__dict__
        order_id = order_model_dict.get('id', 0)
        user_id = str(order_model_dict.get('user_id', ''))
        order_date: datetime = order_model_dict.get('date', datetime.now(timezone.utc))
        if not order_date.tzinfo:
            order_date = order_date.replace(tzinfo=timezone.utc)
        order_comment = order_model_dict.get('comment', '')
        order_buyer_name = order_model_dict.get('buyer_name', '')
        order_buyer_phone = order_model_dict.get('buyer_phone', '')
        delivery_track_number = order_model_dict.get('delivery_track_number', '')
        delivery_track_number = '' if not delivery_track_number else delivery_track_number

        # parsing address
        region_code = order_model_dict.get('region_id', 0)
        region_name = order_model_dict.get('region_name', '')
        city_code = order_model_dict.get('city_id', 0)
        city_name = order_model_dict.get('city_name', '')
        region_code = 0 if not region_code else region_code
        city_code = 0 if not city_code else city_code
        delivery_address = order_model_dict.get('delivery_address', '')
        address_schema = DeliveryAddressSchema(
            region=RegionSchema(code=region_code, name=region_name),
            city=CitySchema(code=city_code, name=city_name),
            address=delivery_address
        )

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
            id = selected_config_dict.get('id', 0)
            ram_amount = selected_config_dict.get('ram_amount', 0)
            ssd_amount = selected_config_dict.get('ssd_amount', 0)
            additional_price = selected_config_dict.get('additional_price', 0)
            is_default = selected_config_dict.get('is_default', False)
            additional_ram = selected_config_dict.get('additional_ram', False)
            soldered_ram = selected_config_dict.get('soldered_ram', 0)

            selected_configuration = ProductConfigurationSchema(
                id=id,
                ram_amount=ram_amount, ssd_amount=ssd_amount,
                additional_price=additional_price, is_default=is_default,
                additional_ram=additional_ram, soldered_ram=soldered_ram
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
            payment_id = order_payment_dict.get('id', 0)
            order_id = order_id
            payment_status = PaymentStatus(order_payment_dict.get('status', 'pending'))
            payment_date: datetime = order_payment_dict.get('date', datetime.now(timezone.utc))
            if not payment_date.tzinfo:
                payment_date = payment_date.replace(tzinfo=timezone.utc)

            payment_schema = PaymentSchema(
                id=payment_id,
                order_id=order_id,
                status=payment_status,
                sum=sum,
                date=payment_date,
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
                delivery_address=address_schema,
                payment=payment_schema,
                delivery_track_number=delivery_track_number
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
                delivery_address=address_schema,
                delivery_track_number=delivery_track_number
            )

        return order_schema

    def get_order_sum(self, order_id: int) -> int:
        order_model = self._repo.get_by_id(order_id)
        if not order_model:
            raise ErrOrderNotFound(order_id)

        # counting order sum
        order_products = self.get_order_products(order_id)
        sum: int = 0
        for order_product in order_products:
            product_price: int = order_product.product.__dict__.get('price', 0)
            additional_price: int = order_product.selected_configuration.__dict__.get('additional_price', 0)
            product_count: int = order_product.__dict__.get('count', 0)

            sum += (product_price + additional_price) * product_count

        return sum

    def get_order_sum_with_delivery(self, order_id: int) -> int:
        order_model = self._repo.get_by_id(order_id)
        if not order_model:
            raise ErrOrderNotFound(order_id)
        order_dict = order_model.__dict__
        order_city_id = order_dict.get('city_id', 0)

        sum = self.get_order_sum(order_id)
        return sum + self._delivery_service.get_shipping_cost(
            order_city_id,
            len(self.get_order_products(order_id))
        )

    def get_by_id(self, order_id: int, user_id: str | None = None) -> OrderSchema:
        order_model = self._repo.get_by_id(order_id)
        if not order_model:
            logger.debug(f'{order_id = }')
            raise ErrOrderNotFound(order_id)

        order_schema = self._order_model_to_schema(order_model)
        if user_id and not order_schema.user_id == user_id:
            raise ErrOrderNotFound(order_id)

        # recalculating order sum with shipping cost
        # if order_schema.delivery_address.city.code:
        #     order_schema.sum += self._delivery_service.get_shipping_cost(
        #         order_schema.delivery_address.city.code, len(order_schema.products)
        #     )

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
        user_products = self._cart_repo.get_user_products(user_id)
        order_model = self._repo.create_with_user_products(user_id, user_products)

        return self._order_model_to_schema(order_model)

    def create_from_cookie_cart(self, cookie_cart: CartInCookie) -> OrderInCookie:
        order_model = self._repo.create_with_cookie_products(cookie_cart.product_list)

        order_schema = self._order_model_to_schema(order_model)
        cookie_order = OrderInCookie(
            id=order_schema.id,
            date=order_schema.date,
            products=[],
            sum=order_schema.sum,
            comment=order_schema.comment,
            buyer_name=order_schema.buyer_name,
            buyer_phone=order_schema.buyer_phone,
            delivery_address=order_schema.delivery_address
        )

        for product in order_schema.products: 
            config_name = f'{product.selected_configuration.ram_amount}GB RAM/{product.selected_configuration.ssd_amount}GB SSD'
            cookie_order_product = CookieOrderProduct(
                product_id=product.product_id,
                product_name=product.product_name,
                configuration_id=product.selected_configuration.id,
                configuration_name=config_name,
                count=product.count
            )
            cookie_order.products.append(cookie_order_product)

        return cookie_order

    def create_user_for_order(self, user: UserCreate) -> UserResponse:
        return self._user_service.create_with_basic_info(user)

    def update_order(self, order_update: OrderUpdateSchema) -> OrderSchema:
        if order_update.user_id:
            logger.debug(f'Updating order with user_id: {order_update.user_id}')

        logger.debug(f'Updating order with schema: {order_update}')
        order_model = self._repo.update(
            order_update.id, order_update.user_id,
            order_update.comment,
            order_update.buyer_name,
            order_update.delivery_address.region.code,
            order_update.delivery_address.region.name,
            order_update.delivery_address.city.code,
            order_update.delivery_address.city.name,
            order_update.delivery_address.address,
            order_update.buyer_phone,
            order_update.delivery_track_number,
        )

        order_schema = self._order_model_to_schema(order_model)
        # recalculating order sum with shipping cost
        # order_schema.sum += self._delivery_service.get_shipping_cost(
        #     order_schema.delivery_address.city.code, len(order_schema.products)
        # )

        logger.debug(f'Updated order: {order_schema}')

        return order_schema

    def remove_order(self, order_id: int, user_id: str) -> None:
        self._repo.remove(order_id, user_id)



def order_service_dependency(
    repo: OrderRepository = Depends(order_repository_dependency),
    cart_repo: CartRepository = Depends(cart_repository_dependency),
    config_repo: ConfigurationRepository = Depends(
        configuration_repository_dependency
    ),
    product_repo: ProductRepository = Depends(product_repository_dependency),
    user_service: UserService = Depends(user_service_dependency),
    delivery_service: DeliveryService = Depends(delivery_service_dependency),
) -> Generator[OrderService, None, None]:

    service = OrderService(repo, cart_repo, config_repo, product_repo, user_service, delivery_service)
    yield service

