from pydantic import BaseModel


class ProductDTO(BaseModel):
    id: int
    name: str
    description: str
    price: int
    count: int | None
    manufacturer_id: int

