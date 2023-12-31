from collections.abc import Generator
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


class CartRepository:
    def __init__(self, db: Session, product_repo: ProductRepository) -> None:
        self._db = db
        self._product_repo = product_repo

    def get_user_products(self, user_id: str) -> list[Product]:
        user_products = (
            self._db.query(UserProduct).filter(
                UserProduct.user_id == user_id).all()
        )
        products = [
            self._product_repo.get_by_id(product.product_id)
            for product in user_products
        ]

        return products


def cart_repository_dependency(
    db: Session = Depends(db_dependency),
    product_repo: ProductRepository = Depends(product_repository_dependency),
) -> Generator[CartRepository, None, None]:
    repo = CartRepository(db, product_repo)
    yield repo


def test_cart_repository():
    session = next(db_dependency())
    repo = CartRepository(session, ProductRepository(session))
    for product in repo.get_user_products('5a354f3f-6818-4695-a8e8-98a2a645cd27'):
        print(product.__dict__)

