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

    soldered_ram: int | None = None
    can_add_ram: bool | None = None
    resolution: str | None = None
    cpu: str | None = None
    gpu: str | None = None
    touch_screen: bool | None = None

