from pydantic import BaseModel


class ConfigurationDTO(BaseModel):
    id: int
    name: str
    additional_price: int

