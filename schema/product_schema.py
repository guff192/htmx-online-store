from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    description: str
    price: int


class Product(ProductBase):
    id: int


class ProductList(BaseModel):
    products: list[Product]

    def get_context(self):
        return self.model_dump()
