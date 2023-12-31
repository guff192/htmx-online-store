from collections.abc import Generator
from typing import Any
from fastapi import Depends
from loguru import logger
from sqlalchemy.orm import Session

from db.session import db_dependency
from models.product import Product
from models.user import UserProduct
from repository.product_repository import (
    ProductRepository,
    product_repository_dependency,
)
from repository.user_repository import (
    UserRepository,
    user_repository_dependency
)


class CartRepository:
    def __init__(
        self, db: Session,
        product_repo: ProductRepository,
        user_repo: UserRepository
    ) -> None:
        self._db = db
        self._product_repo = product_repo
        self._user_repo = user_repo

    def get_user_products(self, user_id: str) -> list[UserProduct]:
        user_products = (
            self._db.query(UserProduct).
            filter(UserProduct.user_id == user_id).all()
        )

        return user_products

    def add_to_cart(self, user_id: str, product_id: int) -> dict[str, Any]:
        user_products = self.get_user_products(user_id)
        product_ids = [
            user_product.product_id for user_product in user_products
        ]

        # Check if product is already in cart
        if product_id not in product_ids:
            user_product = UserProduct(user_id=user_id, product_id=product_id)
            self._db.add(user_product)
        else:
            user_product = list(filter(
                lambda user_product: user_product.product_id == product_id,
                user_products
            ))[0]
            # Increment product count
            user_product.count = user_product.count + 1

        updated_product_dict = user_product.__dict__.copy()
        self._db.commit()

        return updated_product_dict


def cart_repository_dependency(
    db: Session = Depends(db_dependency),
    product_repo: ProductRepository = Depends(product_repository_dependency),
    user_repo: UserRepository = Depends(user_repository_dependency),
) -> Generator[CartRepository, None, None]:
    repo = CartRepository(db, product_repo, user_repo)
    yield repo


def test_cart_repository():
    session = next(db_dependency())
    repo = CartRepository(session, ProductRepository(session), UserRepository(session))
    for product in repo.get_user_products("5a354f3f-6818-4695-a8e8-98a2a645cd27"):
        print(product.__dict__)
