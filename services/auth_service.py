from abc import abstractmethod
from datetime import datetime, timedelta
import time
from typing import Any, Mapping, Protocol

from fastapi import Depends
from google.auth.transport import requests
from google.oauth2 import id_token
from jose import JWTError, jwt
from loguru import logger

from app.config import Settings
from exceptions.auth_exceptions import ErrUserNotFound, ErrWrongCredentials
from repository.user_repository import (
    UserRepository,
    get_user_repository,
    user_repository_dependency,
)
from schema.auth_schema import GoogleOAuthCredentials, OAuthCredentials
from schema.user_schema import UserBase


settings = Settings()


# Using strategy pattern to handle different oauth providers
class OauthProvider(Protocol):
    def __init__(self):
        pass

    @abstractmethod
    def verify_oauth(
        self,
        credential: OAuthCredentials,
    ) -> Mapping[str, Any]:
        pass


class GoogleOAuthProvider(OauthProvider):
    def verify_oauth(
            self, credentials: GoogleOAuthCredentials,
    ) -> Mapping[str, Any]:
        if credentials.form_data.g_csrf_token != credentials.cookie_csrf_token:
            raise ErrWrongCredentials()

        try:
            # geting user info
            id_info: Mapping[str, Any] = id_token.verify_oauth2_token(
                credentials.form_data.credential,
                requests.Request(),
                settings.google_oauth2_client_id,
                int(time.time())
            )

            return id_info
        except Exception as e:
            logger.debug(f'Failed google authentication: {e}')
            raise ErrWrongCredentials()


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
    ):
        self.repo = user_repo

    @property
    def oauth_provider(self) -> OauthProvider:
        return self._provider

    @oauth_provider.setter
    def oauth_provider(self, provider: OauthProvider):
        self._provider = provider

    def verify_oauth(self, credentials: OAuthCredentials) -> Mapping[str, Any]:
        return self._provider.verify_oauth(credentials)

    def create_access_token(
        self,
            data: dict,
            expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=1)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            claims=to_encode,
            key=settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt

    def verify_session_token(self, session_token: str) -> UserBase:
        try:
            payload = jwt.decode(
                token=session_token,
                key=settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
                options={'require_exp': True, 'verify_exp': True},
            )
        except JWTError:
            raise ErrWrongCredentials()

        user_id = payload.get("sub")
        if not user_id:
            raise ErrWrongCredentials()

        user_data = self.repo.get_by_id(user_id)
        if not user_data:
            raise ErrUserNotFound()

        return UserBase(**user_data.__dict__)


def auth_service_dependency(
        user_repo: UserRepository = Depends(user_repository_dependency)
):
    service = AuthService(user_repo)
    yield service


def google_oauth_service_dependency():
    service = GoogleOAuthProvider()
    yield service


def get_auth_service() -> AuthService:
    return AuthService(get_user_repository())

