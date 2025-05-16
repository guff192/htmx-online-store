from typing import Mapping
from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt

from models.manufacturer import Manufacturer
from models.product_configuration import ProductConfiguration


ProductSpecifications = Mapping[str, int | float | str | bool] | None


class Product(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(validation_alias='_id', default=-1)
    name: str = ''

    description: str = ''
    specifications: ProductSpecifications = None

    count: NonNegativeInt = 0
    newcomer: bool = False

    manufacturer: Manufacturer = Manufacturer()

    available_configurations: list[ProductConfiguration] = []
