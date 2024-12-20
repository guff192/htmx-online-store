from abc import abstractmethod
from datetime import datetime, timedelta, timezone
from time import time
from typing import Any, Mapping, Protocol

from fastapi import Depends
from google.auth.transport import requests as google_auth_requests
from google.oauth2 import id_token
from jose import JWTError, jwt
from loguru import logger
import requests

from app.config import Settings
from exceptions.auth_exceptions import ErrUserNotFound, ErrWrongCredentials
from repository.user_repository import (
    UserRepository,
    get_user_repository,
    user_repository_dependency,
)
from schema.auth_schema import (
    GoogleOAuthCredentials,
    OAuthCredentials,
    PhoneLoginForm,
    YandexOauthCredentials
)
from schema.user_schema import LoggedUser
from storage.cache_storage import MemoryCacheStorage


settings = Settings()
cache = MemoryCacheStorage()


# Using strategy pattern to handle different oauth providers
class OauthProvider(Protocol):
    def __init__(self):
        pass

    @abstractmethod
    def verify_oauth(
        self,
        credentials: OAuthCredentials,
    ) -> Mapping[str, Any]:
        pass


class GoogleOAuthProvider(OauthProvider):
    def verify_oauth(
        self,
        credentials: GoogleOAuthCredentials,
    ) -> Mapping[str, Any]:
        if credentials.form_data.g_csrf_token != credentials.cookie_csrf_token:
            raise ErrWrongCredentials()

        try:
            # geting user info
            id_info: Mapping[str, Any] = id_token.verify_oauth2_token(
                credentials.form_data.credential,
                google_auth_requests.Request(),
                settings.google_oauth2_client_id,
                int(time())
            )

            return id_info
        except Exception as e:
            logger.debug(f'Failed google authentication: {e}')
            raise ErrWrongCredentials()


class YandexOAuthProvider(OauthProvider):
    def verify_oauth(
        self,
        credentials: YandexOauthCredentials
    ) -> Mapping[str, Any]:
        if not credentials.expires_in > 0:
            raise ErrWrongCredentials()

        response = requests.get(
            settings.yandex_oauth2_token_uri,
            headers={'Authorization': f'OAuth {credentials.access_token}'},
        )
        try:
            yandex_user_info: Mapping[str, Any] = response.json()
            return yandex_user_info
        except Exception as e:
            logger.debug(f'Failed yandex authentication: {e}')
            raise ErrWrongCredentials()


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
    ):
        self.repo = user_repo

    def init_verification_call(self, phone_form: PhoneLoginForm) -> PhoneLoginForm:
        if not settings.debug:
            logger.debug('Ucaller service is not available in production mode.')
            url = f"https://api.ucaller.ru/v1.0/initCall/"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.ucaller_service_secret_key}.{settings.ucaller_service_id}"
            }
            params = {
                "phone": phone_form.phone,
            }
            response = requests.post(url, headers=headers, params=params)
            if (response_data := response.json())["status"] is False:
                logger.debug(response_data)
                return PhoneLoginForm(phone=phone_form.phone,
                                      error="Не получилось дозвониться на указанный номер.")
        else:
            response_data = {
                "status": True,
                "code": "1234"
            }

        cache.add_value_to_cache(
            key=phone_form.phone,
            value=response_data["code"],
            expires_at=int(time()) + 180)

        return PhoneLoginForm(phone=phone_form.phone)

    def verify_phone_code(self, phone_form: PhoneLoginForm) -> PhoneLoginForm | None:
        code = cache.get_cached_value(phone_form.phone)
        if code != phone_form.code:
            return PhoneLoginForm(phone=phone_form.phone, error="Неверный код.")

        return None

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
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=2)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            claims=to_encode,
            key=settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt

    def verify_session_token(self, session_token: str) -> LoggedUser:
        """
        Verify session token. Either returns found user or raises error.
        """
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

        # parsing user data
        user_data_dict = user_data.__dict__
        name = user_data_dict.get("name", "")
        email = user_data_dict.get("email", "")
        phone = user_data_dict.get("phone", "")
        profile_img_url = user_data_dict.get("profile_img_url", "")
        google_id = user_data_dict.get("google_id", "")
        yandex_id = user_data_dict.get("yandex_id", 0)
        if yandex_id:
            yandex_id = int(yandex_id)
        is_admin = user_data_dict.get("is_admin", False)

        return LoggedUser(
            id=user_id,
            name=name,
            email=email,
            phone=phone,
            profile_img_url=profile_img_url,
            google_id=google_id,
            yandex_id=yandex_id,
            is_admin=is_admin
        )


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

