from collections.abc import Generator

from fastapi import Depends
from loguru import logger
from exceptions.auth_exceptions import ErrUserNotFound
from exceptions.product_exceptions import ErrProductNotFound
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
    ProductList,
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

    def get_cart(self, user_id: str) -> Cart:
        # Get products in user's cart
        orm_product_dicts = map(
            lambda product: product.__dict__,
            self._repo.get_user_products(user_id)
        )
        products: list[ProductInCart] = []
        for product_dict in orm_product_dicts:
            product_id, product_count = \
                product_dict.get('product_id', 0), product_dict.get('count', 0)
            if product_count == 0:
                continue

            product_schema = self._products.get_by_id(product_id).__dict__
            product_in_cart = ProductInCart(
                id=product_id,
                count=product_count,
                name=product_schema.get('name', ''),
                description=product_schema.get('description', ''),
                price=product_schema.get('price', 0),
            )
            products.append(product_in_cart)
        if not products:
            raise ErrProductNotFound()

        # Get user
        orm_user = self._users.get_by_id(user_id)
        if not orm_user:
            raise ErrUserNotFound()
        user_schema = UserResponse(**orm_user.__dict__)

        return Cart(
            product_list=products,
            user=user_schema,
        )

    def add_to_cart(self, user_id: str, product_id: int) -> ProductInCart:
        orm_product_dict = self._repo.add_to_cart(user_id, product_id)
        product_id, product_count = (
            orm_product_dict.get('product_id', 0),
            orm_product_dict.get('count', 0)
        )
        if not product_id:
            logger.debug(orm_product_dict)
            raise ErrProductNotFound()

        product_info = self._products.get_by_id(product_id).__dict__

        product_schema = ProductInCart(
            id=product_id,
            count=product_count,
            name=product_info.get('name', ''),
            description=product_info.get('description', ''),
            price=product_info.get('price', 0),
        )

        return product_schema

    def remove_from_cart(self, user_id: str, product_id: int) -> ProductInCart:
        orm_product_dict = self._repo.remove_from_cart(user_id, product_id)
        if not orm_product_dict:
            raise ErrProductNotFound()

        product_id, product_count = (
            orm_product_dict.get('product_id', 0),
            orm_product_dict.get('count', 0)
        )
        if not product_id:
            raise ErrProductNotFound()

        product_info = self._products.get_by_id(product_id).__dict__
        product_schema = ProductInCart(
            id=product_id,
            count=product_count,
            name=product_info.get('name', ''),
            description=product_info.get('description', ''),
            price=product_info.get('price', 0),
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

