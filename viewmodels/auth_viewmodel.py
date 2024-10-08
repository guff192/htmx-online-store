from typing import Any, Generator, Mapping

from fastapi import Depends

from schema.auth_schema import (
    GoogleOAuthCredentials,
    OAuthCredentials,
    PhoneLoginForm,
    YandexOauthCredentials
)
from services.auth_service import (
    AuthService,
    GoogleOAuthProvider,
    YandexOAuthProvider,
    auth_service_dependency,
    get_auth_service
)


class AuthViewModel:
    def __init__(self, auth_service: AuthService) -> None:
        self._service = auth_service

    def verify_oauth(
            self, credentials: OAuthCredentials
    ) -> Mapping[str, Any] | None:

        # Setup provider
        if isinstance(credentials, GoogleOAuthCredentials):
            self._service.oauth_provider = GoogleOAuthProvider()
        elif isinstance(credentials, YandexOauthCredentials):
            self._service.oauth_provider = YandexOAuthProvider()
        else:
            return None

        return self._service.verify_oauth(credentials)

    def get_phone_code_input(self, phone_form: PhoneLoginForm) -> PhoneLoginForm:
        return self._service.init_verification_call(phone_form)

    def verify_phone_code(self, phone_form: PhoneLoginForm) -> PhoneLoginForm | None:
        return self._service.verify_phone_code(phone_form)

    def create_session(self, data: dict) -> str:
        return self._service.create_access_token(data)


def auth_viewmodel_dependency(
        auth_service: AuthService = Depends(auth_service_dependency)
) -> Generator[AuthViewModel, None, None]:
    vm = AuthViewModel(auth_service)
    yield vm


def get_auth_viewmodel() -> AuthViewModel:
    return AuthViewModel(get_auth_service())

