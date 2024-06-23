from fastapi import HTTPException, status


class ErrPaymentNotFound(HTTPException):
    def __init__(self, payment_id: int | None = None):
        detail = f'Payment {payment_id} not found' if payment_id else 'Payment not found'

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ErrUnsuccessfulPayment(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Payment was not successful'
        )


class ErrInvalidPaymentData(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid payment data'
        )

