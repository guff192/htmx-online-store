from fastapi import Depends
from sqlalchemy.orm import Session

from db.session import db_dependency
from models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Product]:
        return self.db.query(Product).all()

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.query(Product).get(product_id)


def product_repository_dependency(db: Session = Depends(db_dependency)):
    repo = ProductRepository(db)
    yield repo


def test_product_repository():
    session = next(db_dependency())
    repo = ProductRepository(session)
    print(repo.get_by_id(2).__dict__)

