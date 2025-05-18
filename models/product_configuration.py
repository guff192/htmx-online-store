from pydantic import BaseModel
from pydantic_core import Url


class ConfigurationType(BaseModel):
    id: int | None
    name: str
    image_url: Url | None = None


class ProductConfiguration(BaseModel):
    id: int | None = None

    additional_price: int | None = None
    short_name: str | None = None

    type: ConfigurationType
    value: int | float | str | bool
