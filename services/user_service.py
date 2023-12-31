from typing import Any

from fastapi import Depends
from google.auth.jwt import Mapping
from loguru import logger

from exceptions.auth_exceptions import ErrWrongCredentials
from models.user import User
from repository.user_repository import (
    UserRepository,
    get_user_repository,
    user_repository_dependency,
)
from schema.user_schema import UserCreateGoogle, UserResponse


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.repo = user_repo

    def _get_by_google_id(self, google_id: str) -> User | None:
        return self.repo.get_by_google_id(google_id)

    def _parse_user_create_google_schema(
        self, google_user_id_info: Mapping[str, Any]
    ) -> UserCreateGoogle | None:
        try:
            user_schema = UserCreateGoogle(
                google_id=str(google_user_id_info.get("sub", None)),
                name=str(google_user_id_info.get("name", "")),
                profile_img_url=str(google_user_id_info.get("picture")),
                email=str(google_user_id_info.get("email", False)),
                email_verified=bool(
                    google_user_id_info.get("email_verified", False)),
                hd=str(google_user_id_info.get("hd", "")),
            )

            return user_schema
        except Exception as e:
            logger.debug(f"Error parsing user schema: {e}")
            return None

    def get_by_id(self, user_id: str) -> User | None:
        return self.repo.get_by_id(user_id)

    def get_or_create_by_google_id(self, id_info: Mapping[str, Any]) -> UserResponse:
        user_schema = self._parse_user_create_google_schema(id_info)
        if not user_schema:
            raise ErrWrongCredentials()

        if not user_schema.verify():
            raise ErrWrongCredentials()

        user: User | None = self._get_by_google_id(user_schema.google_id)
        if user is None:
            user: User | None = self.repo.create(
                name=user_schema.name,
                profile_img_url=user_schema.profile_img_url,
                google_id=user_schema.google_id
            )

        user_dict = user.__dict__
        user_schema = UserResponse(**user_dict)

        return user_schema


def user_service_dependency(
        user_repo: UserRepository = Depends(user_repository_dependency)
):
    service = UserService(user_repo)
    yield service


def get_user_service() -> UserService:
    return UserService(get_user_repository())

