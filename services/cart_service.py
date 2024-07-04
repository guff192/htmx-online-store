from collections.abc import Generator
from typing import Any

from fastapi import Depends
from loguru import logger
from sqlalchemy import Index
from exceptions.auth_exceptions import ErrUserNotFound
from exceptions.product_exceptions import ErrProductNotFound
from models.product import ProductConfiguration
from models.user import User, UserProduct
from schema.user_schema import UserResponse
from services.user_service import UserService, user_service_dependency
from services.product_service import ProductService, product_service_dependency
from repository.cart_repository import (
    CartRepository,
    cart_repository_dependency
)
from schema.cart_schema import Cart, CartInCookie
from schema.product_schema import (
    ProductInCart, ProductConfiguration as ProductConfigurationSchema,
    Product as ProductSchema
)


class CartService:
    def __init__(
            self,
            repo: CartRepository,
            user_service: UserService,
            product_service: ProductService
    ) -> None:
        self._repo = repo
        self._users = user_service
        self._products = product_service

    def _userproduct_model_to_productincart_schema(
        self,
        userproduct: UserProduct,
        product_id: int = 0
    ) -> ProductInCart:
        if not userproduct:
            logger.debug(f'No userproduct data: {userproduct}')
            return ProductInCart(
                id=product_id,
                count=0,
                name='',
                description='',
                price=0,
                manufacturer_name='',
            )

        product = userproduct.product
        if not product or not hasattr(product, 'manufacturer'):
            logger.debug(f'No product data: {product}')
            return ProductInCart(
                id=product_id,
                count=0,
                name='',
                description='',
                price=0,
                manufacturer_name='',
            )

        manufacturer = product.manufacturer
        if not manufacturer:
            logger.debug(f'No manufacturer data: {product.__dict__}')
            return ProductInCart(
                id=product_id,
                count=0,
                name='',
                description='',
                price=0,
                manufacturer_name='',
            )

        userproduct_orm_dict: dict[str, Any] = userproduct.__dict__
        product_orm_dict: dict[str, Any] = product.__dict__
        product_name = product_orm_dict.get('name', '')
        product_description = product_orm_dict.get('description', '')
        product_count = userproduct_orm_dict.get('count', 0)
        product_price = product_orm_dict.get('price', 0)

        manufacturer_dict: dict[str, Any] = manufacturer.__dict__
        manufacturer_name = manufacturer_dict.get('name', '')

        orm_configs = [self._products.get_config_by_id(config.__dict__['configuration_id'])
                      for config in product.configurations]
        schema_configs = [
            ProductConfigurationSchema(
                id=config.__dict__['id'],
                name=config.__dict__['name'],
                additional_price=config.__dict__['additional_price'],
            ) for config in orm_configs
        ]

        selected_config = userproduct.selected_configuration
        selected_config_schema = ProductConfigurationSchema(
            id=selected_config.__dict__['id'],
            name=selected_config.__dict__['name'],
            additional_price=selected_config.__dict__['additional_price'],
        )

        product_in_cart = ProductInCart(
            id=product_id,
            count=product_count,
            name=product_name,
            description=product_description,
            price=product_price,
            manufacturer_name=manufacturer_name,
            configurations=schema_configs,
            selected_configuration=selected_config_schema,
        )

        return product_in_cart

    def from_cookie_schema(
        self,
        cart_in_cookie: CartInCookie
    ) -> list[ProductInCart]:
        products: list[ProductInCart] = []
        for cookie_product in cart_in_cookie.product_list:
            product = self._products.get_by_id(cookie_product.product_id)

            available_configs = self._products.get_configurations_for_product(product.id)
            try:
                selected_config = list(filter(
                    lambda c: c.id == cookie_product.configuration_id,
                    available_configs
                ))[0]
            except IndexError:
                raise ErrProductNotFound()

            products.append(ProductInCart(
                id=product.id, name=product.name, price=product.price,
                description=product.description, count=cookie_product.count,
                manufacturer_name=product.manufacturer_name,
                configurations=product.configurations,
                selected_configuration=selected_config
            ))
            
        return products

    def get_cart(self, user_id: str) -> Cart:
        '''Get products in user's cart'''
        orm_products = self._repo.get_user_products(user_id)
        products: list[ProductInCart] = []
        for userproduct in orm_products:
            product_id = userproduct.__dict__.get('product_id', 0)
            product = self._userproduct_model_to_productincart_schema(
                userproduct, product_id
            )

            if product:
                products.append(product)

        # Get user info for response
        orm_user: User | None = self._users.get_by_id(user_id)
        if not orm_user:
            raise ErrUserNotFound()
        user_dict = orm_user.__dict__
        user_schema = UserResponse(
            id=user_dict.get('id', ''),
            name=user_dict.get('name', ''),
            email=user_dict.get('email', ''),
            profile_img_url=user_dict.get('profile_img_url', ''),
            google_id=user_dict.get('google_id', ''),
            yandex_id=user_dict.get('yandex_id', 0),
            is_admin=user_dict.get('is_admin', True),
        )

        return Cart(
            product_list=products,
            user=user_schema,
        )

    def get_product_in_cart(self, user_id: str, product_id: int) -> ProductInCart:
        orm_product: UserProduct | None = self._repo.get_product_in_cart(
            user_id, product_id
        )
        product_schema: ProductInCart = (
            self._userproduct_model_to_productincart_schema(orm_product)
        )

        return product_schema

    def add_to_cart(self, user_id: str | None,
                    product_id: int, configuration_id: int) -> ProductInCart:
        if not user_id:
            product_schema: ProductSchema = self._products.get_by_id(product_id)
            product_in_cart = ProductInCart(id=product_schema.id,
                                    name=product_schema.name, 
                                    description=product_schema.description,
                                    price=product_schema.price, count=1,
                                    manufacturer_name=product_schema.manufacturer_name,
                                    configurations=product_schema.configurations,
                                    selected_configuration=product_schema.selected_configuration)

            return product_in_cart

        orm_product: UserProduct | None = (
            self._repo.add_to_cart(user_id, product_id, configuration_id)
        )
        product_schema: ProductInCart = (
            self._userproduct_model_to_productincart_schema(orm_product,
                                                            product_id)
        )

        return product_schema

    def remove_from_cart(self, user_id,
                         configuration_id: int,
                         product_id: int) -> ProductInCart:
        orm_product: UserProduct | None = (
            self._repo.remove_from_cart(user_id, configuration_id, product_id)
        )
        product_schema: ProductInCart = (
            self._userproduct_model_to_productincart_schema(
                orm_product, product_id
            )
        )

        return product_schema


def get_cart_service() -> CartService:
    raise NotImplementedError()


def cart_service_dependency(
        repo: CartRepository = Depends(cart_repository_dependency),
        user_service: UserService = Depends(user_service_dependency),
        product_service: ProductService = Depends(product_service_dependency),
) -> Generator[CartService, None, None]:
    service = CartService(repo, user_service, product_service)

    yield service

