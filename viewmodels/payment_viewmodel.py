from fastapi import Depends
from typing import Generator

from schema.order_schema import OrderWithPaymentSchema, TinkoffWebhookRequest
from services.payment_service import PaymentService, payment_service_dependency


class PaymentViewModel:
    def __init__(
        self, service: PaymentService
    ) -> None:
        self._service = service

    def get_by_order_id(self, order_id: int, user_id: str) -> OrderWithPaymentSchema:
        return self._service.get_order_with_payment(order_id, user_id)

    def update_payment_status(self, request: TinkoffWebhookRequest):
        self._service.update_payment_status(request)


def payment_viewmodel_dependency(
    service: PaymentService = Depends(payment_service_dependency),
) -> Generator[PaymentViewModel, None, None]:
    vm = PaymentViewModel(service)

    yield vm

