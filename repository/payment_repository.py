from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Query, Session

from db.session import db_dependency
from models.payment import Payment


class PaymentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_payment_query(self, order_id: int) -> Query[Payment]:
        return self._session.query(Payment).filter(
            Payment.order_id == order_id,
        )

    def create(self, order_id: int) -> Payment | None:
        payment = Payment(
            order_id=order_id,
            status='pending',
        )

        self._session.add(payment)
        self._session.commit()
        self._session.flush([payment])

        payment = self.get_by_order_id(order_id)

        return payment

    def get_by_order_id(self, order_id: int) -> Payment | None:
        return self._get_payment_query(order_id).first()


def payment_repository_dependency(
    db: Session = Depends(db_dependency),
) -> Generator[PaymentRepository, None, None]:
    repo = PaymentRepository(db)
    yield repo

