from uuid import UUID
from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    email: str
    profile_img_url: str
    google_id: str | None
    yandex_id: int | None
    is_admin: bool = False


class UserResponse(UserBase):
    id: UUID


class LoggedUser(UserBase):
    id: UUID


class UserCreateGoogle(UserBase):
    google_id: str
    email_verified: bool
    hd: str

    def verify(self) -> bool:
        if self.email.endswith('@gmail.com'):
            return True
        elif self.email_verified and self.hd:
            return True

        return False


class UserCreateYandex(UserBase):
    yandex_id: int
    is_avatar_empty: bool

    def verify(self) -> bool:
        if self.email.endswith('@yandex.ru'):
            return True
        elif self.is_avatar_empty:
            return True

        return False

