from uuid import UUID
from pydantic import AliasPath, BaseModel, ConfigDict, Field, NonNegativeInt

from models.product_configuration import ProductConfiguration


class CartProduct(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    product_id: int
    quantity: NonNegativeInt = Field(validation_alias="count")

    name: str | None = Field(
        validation_alias=AliasPath("product", "name"), default=None
    )
    price: int | None = Field(
        validation_alias=AliasPath("product", "price"), default=None
    )
    selected_configurations: list[ProductConfiguration] = Field(
        validation_alias="configurations"
    )


class Cart(BaseModel):
    user_id: UUID
    products: list[CartProduct]
