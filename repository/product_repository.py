from fastapi import Depends
from sqlalchemy.orm import Session

from db.session import db_dependency
from models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, offset: int) -> list[Product]:
        return self.db.query(Product)\
            .order_by(Product.name)\
            .slice(offset, offset + 10)\
            .all()

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.query(Product).get(product_id)

    def get_by_name(self, name: str) -> Product | None:
        return self.db.query(Product).filter(Product.name == name).first()

    def search(self, name: str) -> list[Product]:
        return self.db.query(Product).\
            filter(Product.name.like(f'%{name}%')).all()

    def create(self,
               name: str,
               description: str,
               price: int) -> Product:
        product = Product(name=name, description=description, price=price)
        self.db.begin(nested=True)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self,
               id: int,
               name: str,
               description: str,
               price: int) -> int | None:

        self.db.begin(nested=True)
        updated_count = self.db.query(Product).filter(Product._id == id).update({
            'name': name,
            'description': description,
            'price': price
        })
        self.db.commit()

        return updated_count


def product_repository_dependency(db: Session = Depends(db_dependency)):
    repo = ProductRepository(db)
    yield repo


def test_product_repository():
    session = next(db_dependency())
    repo = ProductRepository(session)
    print(repo.get_by_id(2).__dict__)

