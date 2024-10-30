from pydantic import BaseModel


class ConfigurationDTO(BaseModel):
    id: int
    ram_amount: int
    ssd_amount: int

    additional_price: int

    is_default: bool = False
    additional_ram: bool = False
    soldered_ram: int = 0

