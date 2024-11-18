from enum import Enum
from typing import Any, Sequence

from pydantic import BaseModel

from schema import SchemaUtils
from schema.manufacturer_schema import Manufacturer


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
    ram_amount: int
    ssd_amount: int

    additional_price: int

    is_default: bool = False
    additional_ram: bool = False
    soldered_ram: int = 0

    def __repr__(self) -> str:
        return f'{self.ram_amount}ГБ RAM/{self.ssd_amount}ГБ SSD'

    def __str__(self) -> str:
        return self.__repr__()


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
    soldered_ram: int | None = None
    can_add_ram: bool | None = None
    resolution: str | None = None
    cpu: str | None = None
    gpu: str | None = None
    touch_screen: bool | None = None

    def is_valid(self) -> bool:
        if not self.name or not self.price or not self.configurations:
            return False
        return True


class ProductCreate(ProductBase):
    count: int
    manufacturer_name: str
    resolution_name: str

    def is_valid(self) -> bool:
        return super().is_valid() and self.count > 0


class ProductUpdate(ProductCreate):
    pass


class ProductUpdateResponse(BaseModel):
    count: int


class Product(ProductBase):
    id: int
    manufacturer: Manufacturer
    photos: list[ProductPhotoPath] = []

    @property
    def absolute_url(self) -> str:
        return f'/products/{self.id}'

    @property
    def short_name(self) -> str:
        name_parts = self.name.split(',')
        name, cpu, resolution = name_parts[:3]
        name = name + '\n'
        resolution = name_parts[3] if 'gb' in resolution else resolution
        return ''.join((name, cpu, resolution))

    @property
    def ram_amounts(self) -> set[int]:
        return set(map(lambda c: c.ram_amount, self.configurations))

    @property
    def ssd_amounts(self) -> set[int]:
        return set(map(lambda c: c.ssd_amount, self.configurations))

    @utils.add_shop_to_context
    def build_context(self) -> dict[str, Any]:
        return {'product': self}


class ProductList(BaseModel):
    products: Sequence[Product]
    offset: int = 0

    @utils.add_shop_to_context
    def build_context(self) -> dict[str, Any]:
        return {'products': self.products, 'offset': self.offset}

