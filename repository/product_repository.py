from fastapi import Depends
from sqlalchemy.orm import Session

from db.session import db_dependency
from models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Product]:
        return self.db.query(Product).all()


def get_product_repository(db: Session = Depends(db_dependency)):
    repo = ProductRepository(db)
    yield repo

