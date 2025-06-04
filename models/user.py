from uuid import UUID
from pydantic import BaseModel, ConfigDict
from pydantic_core import Url


UserId = UUID | str


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UserId
    google_id: str | None
    yandex_id: int | None

    name: str
    email: str | None
    phone: str | None

    profile_img_url: Url | None

    is_admin: bool
