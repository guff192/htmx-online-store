from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import Url


class Banner(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(validation_alias='_id')
    name: str
    description: str | None = None
    img_url: Url | None = None
