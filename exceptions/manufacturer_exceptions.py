from fastapi import HTTPException, status


class ErrManufacturerNotFound(HTTPException):
    def __init__(self, manufacturer_identificator: int | str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manufacturer {manufacturer_identificator} not found",
        )
