from pydantic import BaseModel, ConfigDict, Field


class Banner(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(validation_alias='_id')
    name: str
    description: str
    img_url: str
