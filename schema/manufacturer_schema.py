from pydantic import BaseModel


class Manufacturer(BaseModel):
    name: str
    logo_url: str

