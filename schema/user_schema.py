from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    profile_img_url: str
    google_id: str | None
    is_admin: bool = False


class UserCreateGoogle(UserBase):
    google_id: str
    email: str
    email_verified: bool
    hd: str

    def verify(self) -> bool:
        if self.email.endswith('@gmail.com'):
            return True
        elif self.email_verified and self.hd:
            return True

        return False
