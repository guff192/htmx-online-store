from enum import Enum
from typing import Any, Sequence

from pydantic import BaseModel

from schema import SchemaUtils


utils = SchemaUtils()


class ProductPhotoSize(str, Enum):
    large = ''
    small = 'small'
    thumbs = 'thumbs'


class ProductPhotoPath(BaseModel):
    file_name: str
    path: str

    @property
    def full_path(self) -> str:
        return f'{self.path}/{self.file_name}'

    @property
    def large_path(self) -> str:
        return f'{self.path}/{self.file_name}'

    @property
    def small_path(self) -> str:
        return f'{self.path}/small/{self.file_name}'


class ProductConfiguration(BaseModel):
    id: int
    name: str
    additional_price: int


class ProductPrices(BaseModel):
    product_id: int
    basic_price: int
    configurations: list[ProductConfiguration]
    selected_configuration: ProductConfiguration

    def build_context(self) -> dict[str, Any]:
        return self.__dict__


class ProductBase(BaseModel):
    name: str
    description: str
    price: int
    configurations: list[ProductConfiguration] = []
    selected_configuration: ProductConfiguration | None = None

    def is_valid(self) -> bool:
        if not self.name or not self.price or not self.configurations:
            return False
        return True


class ProductCreate(ProductBase):
    count: int
    manufacturer_name: str

    def is_valid(self) -> bool:
        return super().is_valid() \
                and self.manufacturer_name != '' \
                and self.count > 0


class ProductUpdate(ProductCreate):
    count: int
    manufacturer_name: str


class ProductUpdateResponse(BaseModel):
    count: int


class Product(ProductBase):
    id: int
    manufacturer_name: str
    photos: list[ProductPhotoPath] = []

    @property
    def absolute_url(self) -> str:
        return f'/products/{self.id}'

    @utils.add_shop_to_context
    def build_context(self) -> dict[str, Any]:
        return {'product': self}


class ProductInCart(Product):
    count: int 


class ProductList(BaseModel):
    products: Sequence[Product]
    offset: int = 0

    @utils.add_shop_to_context
    def build_context(self) -> dict[str, Any]:
        return {'products': self.products, 'offset': self.offset}

