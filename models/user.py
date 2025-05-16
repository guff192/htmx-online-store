from uuid import UUID
from pydantic import BaseModel
from pydantic_core import Url


UserId = UUID


class User(BaseModel):
    id: UserId
    google_id: str | None
    yandex_id: int | None

    name: str
    email: str | None
    phone: str | None

    profile_img_url: Url | None

    is_admin: bool
