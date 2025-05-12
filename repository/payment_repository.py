from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Query, Session

from db.session import db_dependency
from exceptions.payment_exceptions import ErrPaymentNotFound
from db_models.payment import PaymentDbModel


class PaymentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_payment_by_id_query(self, id) -> Query[PaymentDbModel]:
        return self._session.query(PaymentDbModel).filter(
            PaymentDbModel.id == id
        )

    def _get_payment_by_orderid_query(self, order_id: int) -> Query[PaymentDbModel]:
        return self._session.query(PaymentDbModel).filter(
            PaymentDbModel.order_id == order_id,
        )

    def create(self, order_id: int) -> PaymentDbModel | None:
        payment = PaymentDbModel(
            order_id=order_id,
            status='pending',
        )

        self._session.add(payment)
        self._session.commit()
        self._session.flush([payment])

        payment = self.get_by_order_id(order_id)

        return payment

    def get_by_order_id(self, order_id: int) -> PaymentDbModel | None:
        return self._get_payment_by_orderid_query(order_id).first()

    def update_status_by_id(self, id: int, status: str) -> None:
        payment_query = self._get_payment_by_id_query(id)
        found_payment = payment_query.first()
        if found_payment is None:
            raise ErrPaymentNotFound()

        payment_query.update({PaymentDbModel.status: status})
        self._session.commit()
        self._session.flush([found_payment])


def payment_repository_dependency(
    db: Session = Depends(db_dependency),
) -> Generator[PaymentRepository, None, None]:
    repo = PaymentRepository(db)
    yield repo

