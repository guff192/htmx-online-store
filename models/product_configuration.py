from uuid import UUID
from pydantic import BaseModel
from pydantic_core import Url


class ConfigurationType(BaseModel):
    id: int | None
    name: str
    image_url: Url | None = None


class ConfigurationValue(BaseModel):
    type: ConfigurationType
    value: int | float | str | bool


class ProductConfiguration(BaseModel):
    id: UUID

    additional_price: int | None = None
    short_name: str | None = None

    value: ConfigurationValue
