from collections.abc import Generator
from typing import Any

from fastapi import Depends
from loguru import logger
from sqlalchemy.orm import Query, Session

from db.session import db_dependency
from exceptions.product_exceptions import ErrProductNotFound
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

    def get_user_product(
            self,
            user_id: str,
            product_id: int
    ) -> Query[UserProduct]:
        return (
            self._db
            .query(UserProduct)
            .filter(UserProduct.user_id == user_id)
            .filter(UserProduct.product_id == product_id)
        )

    def get_user_products(self, user_id: str) -> list[UserProduct]:
        user_products = (
            self._db.query(UserProduct).
            filter(UserProduct.user_id == user_id).all()
        )

        return user_products

    def add_to_cart(self, user_id: str, product_id: int) -> dict[str, Any]:
        found_product = self.get_user_product(user_id, product_id)

        # Check if product is already in cart
        if not found_product:
            user_product = UserProduct(user_id=user_id, product_id=product_id)
            self._db.add(user_product)
        else:
            # Increment product count
            found_product.update({UserProduct.count: UserProduct.count + 1})

        self._db.commit()
        updated_product_dict = (
            self
            .get_user_product(user_id, product_id)
            .first()
            .__dict__
            .copy()
        )

        return updated_product_dict

    def remove_from_cart(
            self,
            user_id: str,
            product_id: int
    ) -> dict[str, Any] | None:
        found_product = self.get_user_product(user_id, product_id)
        if not found_product:
            raise ErrProductNotFound()

        if found_product.count == 1:
            self._db.delete(found_product)
            return
        else:
            found_product.update({UserProduct.count: UserProduct.count - 1})

        self._db.commit()
        updated_product_dict = (
            self
            .get_user_product(user_id, product_id)
            .first()
            .__dict__
            .copy()
        )

        return updated_product_dict


def cart_repository_dependency(
    db: Session = Depends(db_dependency),
    product_repo: ProductRepository = Depends(product_repository_dependency),
    user_repo: UserRepository = Depends(user_repository_dependency),
) -> Generator[CartRepository, None, None]:
    repo = CartRepository(db, product_repo, user_repo)
    yield repo


def test_cart_repository():
    USER_ID = '5a354f3f-6818-4695-a8e8-98a2a645cd27'
    PRODUCT_ID = 13
    session = next(db_dependency())
    repo = CartRepository(
        session,
        ProductRepository(session),
        UserRepository(session)
    )
    logger.debug(repo.remove_from_cart(USER_ID, PRODUCT_ID))

