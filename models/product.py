from typing import Mapping
from pydantic import BaseModel, NonNegativeInt

from manufacturer import Manufacturer
from product_configuration import ProductConfiguration


ProductSpecifications = Mapping[str, int | float | str | bool] | None


class Product(BaseModel):
    id: int
    name: str

    description: str
    specifications: ProductSpecifications

    count: NonNegativeInt
    newcomer: bool

    manufacturer: Manufacturer

    available_configurations: list[ProductConfiguration]
