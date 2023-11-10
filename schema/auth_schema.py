from pydantic import BaseModel


class OAuthCredentials(BaseModel):
    pass


class GoogleLoginForm(BaseModel):
    credential: str
    g_csrf_token: str


class GoogleOAuthCredentials(OAuthCredentials):
    form_data: GoogleLoginForm
    cookie_csrf_token: str
