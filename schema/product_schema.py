from typing import Any

from pydantic import BaseModel

from schema import SchemaUtils


utils = SchemaUtils()


class ProductBase(BaseModel):
    name: str
    description: str
    price: int

    def validate(self) -> bool:
        if not self.name or not self.price:
            return False
        return True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductUpdateResponse(BaseModel):
    count: int


class Product(ProductBase):
    id: int

    @property
    def absolute_url(self) -> str:
        return f'/products/{self.id}'

    @utils.add_shop_to_context
    def build_context(self) -> dict[str, Any]:
        return {'product': self}


class ProductList(BaseModel):
    products: list[Product]

    @utils.add_shop_to_context
    def build_context(self) -> dict[str, Any]:
        return {'products': self.products}

