from collections.abc import Generator
from typing import Any

from fastapi import Depends
from loguru import logger
from exceptions.auth_exceptions import ErrUserNotFound
from models.product import ProductConfiguration
from models.user import User, UserProduct
from schema.user_schema import UserResponse
from services.user_service import UserService, user_service_dependency
from services.product_service import ProductService, product_service_dependency
from repository.cart_repository import (
    CartRepository,
    cart_repository_dependency
)
from schema.cart_schema import Cart
from schema.product_schema import (
    ProductInCart, ProductConfiguration as ProductConfigurationSchema
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
        user_schema = UserResponse(**user_dict)

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

    def add_to_cart(self, user_id: str,
                    product_id: int, configuration_id: int) -> ProductInCart:
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

