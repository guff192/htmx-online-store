from uuid import UUID
from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    email: str
    profile_img_url: str | None = None
    phone: str | None = None
    google_id: str | None = None
    yandex_id: int | None = None
    is_admin: bool = False


class UserResponse(UserBase):
    id: UUID


class LoggedUser(UserBase):
    id: UUID


class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    id: UUID


class UserCreatePhone(UserCreate):
    phone: str


class UserCreateGoogle(UserCreate):
    google_id: str
    email_verified: bool
    hd: str

    def verify(self) -> bool:
        if self.email.endswith('@gmail.com'):
            return True
        elif self.email_verified and self.hd:
            return True

        return False


class UserCreateYandex(UserCreate):
    yandex_id: int
    is_avatar_empty: bool

    def verify(self) -> bool:
        # No need additional verification
        return True

