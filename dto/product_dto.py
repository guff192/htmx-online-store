from pydantic import BaseModel

from dto.configuration_dto import ConfigurationDTO


class ProductDTO(BaseModel):
    id: int
    name: str
    description: str
    price: int
    count: int
    manufacturer_id: int
    configurations: list[ConfigurationDTO]
    selected_configuration: ConfigurationDTO | None

