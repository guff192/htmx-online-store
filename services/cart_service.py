from collections.abc import Generator

from fastapi import Depends
from loguru import logger
from exceptions.auth_exceptions import ErrUserNotFound
from exceptions.product_exceptions import ErrProductNotFound
from schema.user_schema import UserResponse
from services.user_service import UserService, user_service_dependency
from repository.cart_repository import CartRepository, cart_repository_dependency
from schema.cart_schema import Cart
from schema.product_schema import ProductList, Product as ProductSchema


class CartService:
    def __init__(self, repo: CartRepository, user_service: UserService) -> None:
        self._repo = repo
        self._user_service = user_service

    def get_cart(self, user_id: str) -> Cart:
        orm_product_dicts = map(lambda product: product.__dict__, self._repo.get_user_products(user_id))
        products = [
            ProductSchema(
                id=orm_product.get("_id", 0),
                name=orm_product.get("name", ""),
                description=orm_product.get("description", ""),
                price=orm_product.get("price", 0),
            )
            for orm_product in orm_product_dicts
        ]
        if not products:
            raise ErrProductNotFound()
        product_list = ProductList(products=products, offset=0)

        orm_user = self._user_service.get_by_id(user_id)
        if not orm_user:
            raise ErrUserNotFound()
        user_schema = UserResponse(**orm_user.__dict__)

        return Cart(
            product_list=product_list,
            user=user_schema,
        )

    def add_to_cart(self, product_id: int):
        raise NotImplementedError()

    def remove_from_cart(self, product_id: int):
        raise NotImplementedError()


def get_cart_service() -> CartService:
    raise NotImplementedError()


def cart_service_dependency(
        repo: CartRepository = Depends(cart_repository_dependency),
        user_service: UserService = Depends(user_service_dependency),
) -> Generator[CartService, None, None]:
    service = CartService(repo, user_service)

    yield service

