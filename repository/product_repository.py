from fastapi import Depends
from loguru import logger
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from db.session import db_dependency
from dto.product_dto import ProductDTO
from models.product import Manufacturer, Product
from models.user import UserProduct


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, offset: int) -> list[ProductDTO]:
        orm_product_dicts = map(
            lambda p: p.__dict__ if p else {},
            self.db.query(Product).slice(offset, offset + 10).all()
        )

        dto_list: list[ProductDTO] = []
        for product_dict in orm_product_dicts:
            manufacturer_id = product_dict.get('manufacturer_id', 0)
            manufacturer_id = manufacturer_id if manufacturer_id else 0
            dto_list.append(
                ProductDTO(
                    id=product_dict.get('_id', 0),
                    name=product_dict.get('name', ''),
                    description=product_dict.get('description', ''),
                    price=product_dict.get('price', 0),
                    count=product_dict.get('count', 0),
                    manufacturer_id=manufacturer_id,
                )
            )

        return dto_list

    def get_all_with_cart_info(
        self,
        user_id: str,
        offset: int
    ) -> list[ProductDTO]:
        result: list[ProductDTO] = []

        # Create query
        stmt = (
            select(Product._id, Product.name, Product.description,
                   Product.price, Product.manufacturer_id, UserProduct.count).
            join(UserProduct,  # joining for getting count from user_product
                 Product._id == UserProduct.product_id,
                 isouter=True).
            filter(  # filtering products in cart and products without user
                or_(UserProduct.user_id == user_id,
                    UserProduct.user_id == None)
            ).
            filter(Product.count > 0).
            order_by(Product.name).
            slice(offset, offset + 10)
        )

        # Execute and add to result
        for row in self.db.execute(stmt).all():
            id_, name, description, price, manufacturer_id, = \
                row[0], row[1], row[2], row[3], row[4]
            user_count = row[5]

            product = ProductDTO(
                id=id_, name=name, description=description,
                price=price, count=user_count,
                manufacturer_id=manufacturer_id
            )
            logger.debug(product)
            result.append(product)

        return result

    def get_newcomers(self, offset: int) -> list[Product]:
        product_list = (
            self.db.query(Product).
            filter(Product.newcomer == True).
            slice(offset, offset + 10).all()
        )

        return product_list


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
               price: int,
               count: int = 0,
               manufacturer: Manufacturer | None = None) -> Product:
        product = Product(
            name=name,
            description=description,
            price=price,
            count=count,
            manufacturer=manufacturer,
        )
        self.db.begin(nested=True)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self,
               id: int,
               name: str,
               description: str,
               price: int,
               count: int,
               manufacturer: Manufacturer) -> int:

        transaction = self.db.begin(nested=True)
        updated_product_query = self.db.query(Product).filter(
            Product._id == id
        )

        updated_count = updated_product_query.update({
            'name': name,
            'description': description,
            'price': price,
            'count': count,
            'manufacturer_id': manufacturer.id
        })
        transaction.commit()

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

