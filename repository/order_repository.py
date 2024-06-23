from typing import Generator

from fastapi import Depends
from loguru import logger
from sqlalchemy.orm import Query, Session
from db.session import db_dependency
from exceptions.order_exceptions import ErrOrderNotFound
from models.order import Order, OrderProduct
from models.user import UserProduct


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _user_product_to_order_product(
        self,
        order_id,
        user_product: UserProduct
    ) -> OrderProduct:
        return OrderProduct(order_id=order_id,
                            product_id=user_product.product_id,
                            count=user_product.count,
                            selected_configuration_id=user_product.selected_configuration_id)
    
    def _get_order_query(self, order_id: int) -> Query[Order]:
        return self._session.query(Order).filter(Order.id == order_id)

    def _get_order_product_query(self, order_id: int,
                                 product_id: int) -> Query[OrderProduct]:
        return self._session.query(OrderProduct).filter(
            OrderProduct.order_id == order_id,
            OrderProduct.product_id == product_id
        )

    def get_by_id(self, order_id) -> Order | None:
        return self._get_order_query(order_id).first()

    def list_user_orders(self, user_id: str) -> list[Order]:
        return self._session.query(Order).filter(
            Order.user_id == user_id
        ).order_by(Order.date.desc()).all()

    def get_order_products(self, order_id) -> list[OrderProduct]:
        return self._session.query(OrderProduct).filter(
            OrderProduct.order_id == order_id
        ).all()

    def create(self,
               user_id: str,
               user_products: list[UserProduct]) -> Order:
        logger.info(f'Creating order for user {user_id}')
        order = Order(user_id=user_id, comment='',
                      buyer_name='', buyer_phone='', delivery_address='')
        self._session.add(order)
        self._session.flush([order])

        order_products: list[OrderProduct] = []
        for user_product in user_products:
            order_product = self._user_product_to_order_product(order.id,
                                                                 user_product)
            self._session.add(order_product)
            order_products.append(order_product)

        self._session.commit()
        self._session.flush(order_products)

        order = self.get_by_id(order.id)

        return order

    def update(self, order_id: int, user_id: str,
               comment: str, buyer_name: str, delivery_address: str,
               buyer_phone: str) -> Order:
        found_order_query = self._get_order_query(order_id)

        found_order = found_order_query.first()
        if not found_order or not str(found_order.user_id) == user_id:
            raise ErrOrderNotFound(order_id)

        logger.debug({
            'comment': comment,
            'buyer_name': buyer_name,
            'delivery_address': delivery_address,
            'buyer_phone': buyer_phone
        })
        found_order_query.update({
            Order.comment: comment,
            Order.buyer_name: buyer_name,
            Order.delivery_address: delivery_address,
            Order.buyer_phone: buyer_phone
        })
        self._session.commit()
        self._session.flush([found_order])

        updated_order = self.get_by_id(order_id)

        return updated_order

    def remove(self, order_id: int, user_id: str) -> None:
        found_order_query = self._get_order_query(order_id)
        found_order = found_order_query.first()
        if not found_order or not str(found_order.user_id) == user_id:
            raise ErrOrderNotFound(order_id)

        found_order_products = self.get_order_products(order_id)
        for order_product in found_order_products:
            found_product_query = self._get_order_product_query(
                order_product.order_id, order_product.product_id
            )
            found_product = found_product_query.first()
            found_product_query.delete()
            self._session.flush([found_product])

        found_order_query.delete()
        self._session.flush([found_order])
        self._session.commit()


def order_repository_dependency(
    db: Session = Depends(db_dependency),
) -> Generator[OrderRepository, None, None]:
    repo = OrderRepository(db)
    try:
        yield repo
    finally:
        db.close()


def test_order_repository():
    repo = OrderRepository(next(db_dependency()))

    repo.create('066b2931e8b4417b9801e6f89ab19b30', [
        UserProduct(
            user_id='066b2931e8b4417b9801e6f89ab19b30',
            product_id=1,
            count=1,
            selected_configuration_id=1
        ),
    ])

