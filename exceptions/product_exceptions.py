from fastapi import HTTPException, status


class ErrProductAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail='Product already exists'
        )


class ErrInvalidProduct(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid product data'
        )


class ErrProductNotFound(HTTPException):
    def __init__(self, product_id: int | None = None):
        err_detail = f'Product {product_id} not found' if product_id else 'Product not found'
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=err_detail
        )

