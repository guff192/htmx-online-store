from fastapi import HTTPException, status


class ErrProductAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail='Product already exists'
        )


class ErrInvalidProduct(HTTPException):
    def __init__(self, product_id: int | None = None):
        detailed_msg = "Invalid product data"
        if product_id is not None:
            detailed_msg += f": {product_id}"

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detailed_msg
        )


class ErrProductNotFound(HTTPException):
    def __init__(self, product_id: int | None = None):
        err_detail = f'Product {product_id} not found' if product_id else 'Product not found'
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=err_detail
        )

