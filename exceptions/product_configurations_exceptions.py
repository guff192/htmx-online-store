from fastapi import HTTPException


class ErrProductConfigurationNotFound(HTTPException):
    def __init__(self, config_id: int | None = None):
        detailed_msg = "Product configuration not found"
        if config_id is not None:
            detailed_msg += f": {config_id}"

        super().__init__(status_code=404, detail=detailed_msg)


class ErrInvalidProductConfiguration(HTTPException):
    def __init__(self, config_id: int | None = None):
        detailed_msg = "Invalid product configuration data"
        if config_id is not None:
            detailed_msg += f": {config_id}"

        super().__init__(status_code=400, detail="Invalid product configuration data")
