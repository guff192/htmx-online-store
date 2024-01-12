from loguru import logger
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.session import db_dependency
from dto.product_dto import ProductDTO
from models.product import Product
from models.user import UserProduct


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, offset: int) -> list[ProductDTO]:
        logger.debug('Getting products without user info')
        return [
            ProductDTO(
                id=orm_product.__dict__.get('_id', 0),
                name=orm_product.__dict__.get('name', ''),
                description=orm_product.__dict__.get('description', ''),
                price=orm_product.__dict__.get('price', 0),
                count=None
            ) for orm_product in
            self.db.query(Product)
            .order_by(Product.name)
            .slice(offset, offset + 10)
            .all()
        ]

    def get_all_with_cart_info(
        self,
        user_id: str,
        offset: int
    ) -> list[ProductDTO]:
        logger.debug(f'Getting products for user {user_id}')
        result: list[ProductDTO] = []

        stmt = (
            select(
                Product._id,
                Product.name,
                Product.description,
                Product.price,
                UserProduct.count,
                UserProduct.user_id
            ).
            join(UserProduct, isouter=True).
            slice(offset, offset + 10)
        )
        for row in self.db.execute(stmt).all():
            id_ = row[0]
            name = row[1]
            description = row[2]
            price = row[3]
            count = row[4] if row[4] and str(row[5]) == user_id else None

            product = ProductDTO(
                id=id_,
                name=name,
                description=description,
                price=price,
                count=count
            )
            result.append(product)

        return result

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
    USER_ID = 'a7e02df8-e3d8-4aa5-bc52-ce70fb214647'
    session = next(db_dependency())
    repo = ProductRepository(session)

    for product in repo.get_all_with_cart_info(USER_ID, 10):
        print(product.__dict__)

