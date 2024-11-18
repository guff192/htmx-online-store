from typing import Any
from pydantic import BaseModel


class PhoneLoginForm(BaseModel):
    phone: str
    error: str | None = None
    code: str | None = None

    def build_context(self) -> dict[str, Any]:
        context_dict = self.__dict__
        del context_dict['code']
        return context_dict


class GoogleLoginForm(BaseModel):
    credential: str
    g_csrf_token: str


class OAuthCredentials(BaseModel):
    pass


class GoogleOAuthCredentials(OAuthCredentials):
    form_data: GoogleLoginForm
    cookie_csrf_token: str


class YandexOauthCredentials(OAuthCredentials):
    access_token: str
    token_type: str
    expires_in: int

