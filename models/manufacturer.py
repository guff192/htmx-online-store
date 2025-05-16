from pydantic import BaseModel, ConfigDict


class Manufacturer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str = ''
    logo_url: str | None = None

