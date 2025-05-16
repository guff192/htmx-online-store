from pydantic import BaseModel


class Manufacturer(BaseModel):
    id: int | None
    name: str
    logo_url: str | None

