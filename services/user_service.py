from typing import Any
from uuid import uuid4

from fastapi import Depends
from google.auth.jwt import Mapping
from loguru import logger
from sqlalchemy.exc import IntegrityError
from app.config import Settings

from exceptions.auth_exceptions import ErrUserInvalid, ErrWrongCredentials
from models.user import User
from repository.user_repository import (
    UserRepository,
    get_user_repository,
    user_repository_dependency,
)
from schema.auth_schema import PhoneLoginForm
from schema.user_schema import UserCreate, UserCreateGoogle, UserCreatePhone, UserCreateYandex, UserResponse, UserUpdate


settings = Settings()


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.repo = user_repo
        self._shop_url = settings.shop_public_url.host

    def user_model_to_userresponse_schema(
        self, user_model: User
    ) -> UserResponse:
        user_model_dict = user_model.__dict__
        user_id = user_model_dict.get("id", 0)
        name = user_model_dict.get("name", "")
        email = user_model_dict.get("email", "")
        profile_img_url = user_model_dict.get("profile_img_url", "")
        google_id = user_model_dict.get("google_id")
        yandex_id = user_model_dict.get("yandex_id")

        return UserResponse(
            id=user_id,
            name=name,
            email=email,
            profile_img_url=profile_img_url if profile_img_url else "",
            google_id=google_id,
            yandex_id=yandex_id,
        )


    def _get_by_google_id(self, google_id: str) -> User | None:
        return self.repo.get_by_google_id(google_id)

    def _get_by_yandex_id(self, yandex_id: int) -> User | None:
        return self.repo.get_by_yandex_id(yandex_id)

    def _parse_user_create_phone_schema(
        self, phone_login_form: PhoneLoginForm
    ) -> UserCreatePhone | None:
        try:
            user_schema = UserCreatePhone(
                name='Пользователь без имени',
                email='noemail@noemail.com',
                phone=str(phone_login_form.phone),
            )
            return user_schema
        except Exception as e:
            logger.debug(f"Error parsing user schema: {e}")
            return None

    def _parse_user_create_google_schema(
        self, google_user_id_info: Mapping[str, Any]
    ) -> UserCreateGoogle | None:
        try:
            user_schema = UserCreateGoogle(
                google_id=str(google_user_id_info.get("sub", None)),
                yandex_id=None,
                name=str(google_user_id_info.get("name", "")),
                profile_img_url=str(google_user_id_info.get("picture")),
                email=str(google_user_id_info.get("email", False)),
                email_verified=bool(
                    google_user_id_info.get("email_verified", False)
                ),
                hd=str(google_user_id_info.get("hd", "")),
            )

            return user_schema
        except Exception as e:
            logger.debug(f"Error parsing user schema: {e}")
            return None

    def _parse_user_create_yandex_schema(
        self, yandex_user_id_info: Mapping[str, Any]
    ) -> UserCreateYandex | None:
        try:
            is_avatar_empty = bool(
                yandex_user_id_info.get("is_avatar_empty", False)
            )

            profile_img_url: str = ""
            if not is_avatar_empty:
                profile_img_url = (
                    str(settings.yandex_avatars_base_url)
                    + yandex_user_id_info.get("default_avatar_id", "")
                    + settings.yandex_avatars_default_size
                ) 

            user_schema = UserCreateYandex(
                yandex_id=yandex_user_id_info.get("id", None),
                google_id=None,
                name=str(yandex_user_id_info.get("real_name", "")),
                profile_img_url=profile_img_url,
                email=str(yandex_user_id_info.get("default_email", False)),
                is_avatar_empty=is_avatar_empty,
            )

            return user_schema
        except Exception as e:
            logger.debug(f"Error parsing user schema: {e}")
            return None

    def get_by_email(self, email: str) -> User | None:
        return self.repo.get_by_email(email)

    def get_by_id(self, user_id: str) -> User | None:
        return self.repo.get_by_id(user_id)

    def get_or_create_by_phone(
        self,
        phone: str
    ) -> UserResponse:
        user_model = self.repo.get_by_phone(phone)
        if not user_model:
            user_name = f"Пользователь с номером {phone}"
            user_email = f"{str(uuid4()).split('-')[0]}@{settings.shop_public_url.host}"
            user_model = self.repo.create(
                name=user_name,
                email=user_email,
                phone=phone
            )

        user_schema = self.user_model_to_userresponse_schema(user_model)
        return user_schema

    def get_or_create_by_yandex_id(
        self,
        id_info: Mapping[str, Any]
    ) -> UserResponse:
        user_schema = self._parse_user_create_yandex_schema(id_info)
        if not user_schema or not user_schema.verify():
            raise ErrWrongCredentials()

        user: User | None = self._get_by_yandex_id(user_schema.yandex_id)
        if not user:
            user: User | None = self.repo.create(
                name=user_schema.name,
                email=user_schema.email,
                profile_img_url=user_schema.profile_img_url,
                yandex_id=user_schema.yandex_id,
                google_id=None
            )

        return self.user_model_to_userresponse_schema(user)

    def get_or_create_by_google_id(
        self,
        id_info: Mapping[str, Any]
    ) -> UserResponse:
        user_schema = self._parse_user_create_google_schema(id_info)
        if not user_schema or not user_schema.verify():
            raise ErrWrongCredentials()

        user: User | None = self._get_by_google_id(user_schema.google_id)
        if user is None:
            user: User | None = self.repo.create(
                name=user_schema.name,
                email=user_schema.email,
                profile_img_url=user_schema.profile_img_url,
                google_id=user_schema.google_id
            )

        return self.user_model_to_userresponse_schema(user)

    def create_with_basic_info(
        self,
        user_create_schema: UserCreate
    ) -> UserResponse:
        try:
            user_model =  self.repo.create(
                user_create_schema.name,
                user_create_schema.email
            )
        except IntegrityError as e:
            logger.error(e)
            raise ErrUserInvalid

        return self.user_model_to_userresponse_schema(user_model)

    def update(
        self,
        user_update_schema: UserUpdate
    ) -> UserResponse:
        user_model = self.repo.update(
            user_update_schema.id,
            user_update_schema.name,
            user_update_schema.email,
        )

        return self.user_model_to_userresponse_schema(user_model)


def user_service_dependency(
    user_repo: UserRepository = Depends(user_repository_dependency)
):
    service = UserService(user_repo)
    yield service


def get_user_service() -> UserService:
    return UserService(get_user_repository())

