from typing import Any, Mapping

from fastapi import Depends

from schema.auth_schema import GoogleOAuthCredentials, OAuthCredentials
from services.auth_service import (
    AuthService, GoogleOAuthProvider, get_auth_service
)


class AuthViewModel:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def verify_oauth(self, credentials: OAuthCredentials) -> Mapping[str, Any] | None:
        # Setup provider
        if isinstance(credentials, GoogleOAuthCredentials):
            self.auth_service.oauth_provider = GoogleOAuthProvider()
        else:
            return None

        return self.auth_service.verify_oauth(credentials)


def auth_viewmodel_dependency(auth_service: AuthService = Depends(AuthService)):
    vm = AuthViewModel(auth_service)
    yield vm


def get_auth_viewmodel() -> AuthViewModel:
    return AuthViewModel(get_auth_service())

