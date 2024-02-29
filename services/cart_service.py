from collections.abc import Generator
from typing import Any

from fastapi import Depends
from loguru import logger
from exceptions.auth_exceptions import ErrUserNotFound
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
    ProductInCart,
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
        userproduct: UserProduct | None,
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

        orm_dict: dict[str, Any] = userproduct.__dict__
        product_orm_dict: dict[str, Any] = product.__dict__
        manufacturer_dict: dict[str, Any] = manufacturer.__dict__

        product_in_cart = ProductInCart(
            id=orm_dict.get('product_id', 0),
            count=orm_dict.get('count', 0),
            name=product_orm_dict.get('name', ''),
            description=product_orm_dict.get('description', ''),
            price=product_orm_dict.get('price', 0),
            manufacturer_name=manufacturer_dict.get('name', ''),
        )

        return product_in_cart

    def get_cart(self, user_id: str) -> Cart:
        # Get products in user's cart
        orm_products: list[UserProduct] = self._repo.get_user_products(user_id)
        products: list[ProductInCart] = [
            self._userproduct_model_to_productincart_schema(userproduct)
            for userproduct in orm_products
        ]
        products: list[ProductInCart] = []
        for userproduct in orm_products:
            product_id: int = userproduct.__dict__.get('product_id', 0)
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
        user_dict['yandex_id'] = str(user_dict['yandex_id'])
        user_schema = UserResponse(**user_dict)

        return Cart(
            product_list=products,
            user=user_schema,
        )

    def add_to_cart(self, user_id: str, product_id: int) -> ProductInCart:
        orm_product: UserProduct | None = (
            self._repo.add_to_cart(user_id, product_id)
        )
        product_schema: ProductInCart = (
            self._userproduct_model_to_productincart_schema(orm_product)
        )

        return product_schema

    def remove_from_cart(self, user_id: str, product_id: int) -> ProductInCart:
        orm_product: UserProduct | None = (
            self._repo.remove_from_cart(user_id, product_id)
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

