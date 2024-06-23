from datetime import datetime
from typing import Generator

from fastapi import Depends
from loguru import logger

from exceptions.payment_exceptions import ErrInvalidPaymentData, ErrPaymentNotFound
from models.payment import Payment
from repository.payment_repository import PaymentRepository, payment_repository_dependency
from schema.order_schema import (
    PaymentSchema, PaymentStatus, OrderWithPaymentSchema, TinkoffWebhookRequest
)
from services.order_service import OrderService, order_service_dependency


class PaymentService:
    def __init__(self, repo: PaymentRepository,
                 order_service: OrderService) -> None:
        self._repo = repo
        self._order_service = order_service

    def _payment_model_to_schema(self, payment_model: Payment) -> PaymentSchema:
        # getting data from model
        payment_model_dict = payment_model.__dict__

        payment_id = payment_model_dict.get('id', 0)
        order_id = payment_model_dict.get('order_id', 0)
        status = payment_model_dict.get('status', 'pending')
        date = payment_model_dict.get('date', datetime.now())

        order_sum = self._order_service.get_order_sum(order_id)

        payment_schema = PaymentSchema(
            id=payment_id,
            order_id=order_id,
            sum=order_sum,
            status=PaymentStatus(status),
            date=date
        )

        return payment_schema
    
    def get_by_order_id(self, order_id: int, user_id: str) -> PaymentSchema:
        payment_model = self._repo.get_by_order_id(order_id)
        if payment_model is None:
            raise ErrPaymentNotFound()

        order_schema = self._order_service.get_by_id(payment_model.order_id,
                                                    user_id)
        if order_schema.user_id != user_id:
            raise ErrPaymentNotFound()

        payment_schema = self._payment_model_to_schema(payment_model)

        return payment_schema

    def get_or_create_by_order_id(self, order_id: int, user_id: str) -> PaymentSchema:
        try:
            payment_schema = self.get_by_order_id(order_id, user_id)
        except ErrPaymentNotFound:
            order_schema = self._order_service.get_by_id(order_id, user_id)
            if order_schema.user_id != user_id:
                raise ErrPaymentNotFound()
            
            payment_model = self._repo.create(order_id)
            if not payment_model:
                raise ErrPaymentNotFound()

            payment_schema = self._payment_model_to_schema(payment_model)

        return payment_schema

    def get_order_with_payment(self, order_id: int, user_id: str) -> OrderWithPaymentSchema:
        payment_schema = self.get_or_create_by_order_id(order_id, user_id)
        if payment_schema is None:
            raise ErrPaymentNotFound()

        order_schema = self._order_service.get_by_id(order_id, user_id)

        return OrderWithPaymentSchema(
            id=order_schema.id,
            user_id=order_schema.user_id,
            date=order_schema.date,
            products=order_schema.products,
            sum=order_schema.sum,
            comment=order_schema.comment,
            buyer_name=order_schema.buyer_name,
            buyer_phone=order_schema.buyer_phone,
            delivery_address=order_schema.delivery_address,
            payment=payment_schema
        )

    def update_payment_status(self, schema: TinkoffWebhookRequest):
        if not schema.is_valid():
            logger.debug(f'Invalid schema: {schema}')
            raise ErrInvalidPaymentData

        try:
            payment_model = self._repo.get_by_order_id(int(schema.order_id))
        except ValueError:
            logger.debug(f'Invalid order_id: {schema.order_id} (type: {type(schema.order_id)})')
            raise ErrInvalidPaymentData

        if payment_model is None:
            logger.debug(f'Payment not found for order_id: {schema.order_id}')
            raise ErrPaymentNotFound

        payment_model_dict = payment_model.__dict__
        payment_id = payment_model_dict.get('id', 0)
        order_id = payment_model_dict.get('order_id', 0)
        if order_id != int(schema.order_id):
            logger.debug(f'Invalid order_id: {schema.order_id}, should be: {order_id}')
            raise ErrInvalidPaymentData

        payment_amount = self._order_service.get_order_sum(order_id)
        request_amount = int(schema.amount)
        if payment_amount * 100 != request_amount:
            logger.debug(f'Invalid amount: {request_amount}, should be: {payment_amount*100}')
            raise ErrInvalidPaymentData

        self._repo.update_status_by_id(payment_id, PaymentStatus.success.value)


def payment_service_dependency(
    repo: PaymentRepository = Depends(payment_repository_dependency),
    order_service: OrderService = Depends(order_service_dependency),
) -> Generator[PaymentService, None, None]:
    vm = PaymentService(repo, order_service)

    yield vm

