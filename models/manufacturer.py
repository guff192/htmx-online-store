from pydantic import BaseModel, ConfigDict
from pydantic_core import Url


class Manufacturer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str = ''
    logo_url: Url | None = None

