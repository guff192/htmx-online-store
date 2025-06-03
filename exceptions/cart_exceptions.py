from fastapi import HTTPException, status


class ErrCartProductNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            "Product not found in user's cart",
        )


class ErrCantAddProductToCart(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Product can't be added to cart",
        )
