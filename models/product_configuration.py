from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt
from pydantic_core import Url


class ConfigurationType(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None
    name: str
    image_url: Url | None = None


class ProductConfiguration(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None

    additional_price: NonNegativeInt | None = None
    short_name: str | None = None

    type: ConfigurationType = Field(validation_alias='configuration_type')
    value: int | float | str | bool
