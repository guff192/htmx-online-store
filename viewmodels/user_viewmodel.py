from typing import Any, Generator, Mapping

from fastapi import Depends

from schema.user_schema import UserResponse, UserUpdate
from services.user_service import (
    UserService,
    get_user_service,
    user_service_dependency,
)


class UserViewModel:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    def get_by_google_id_or_create(
        self, id_info: Mapping[str, Any]
    ) -> UserResponse:
        return self.user_service.get_or_create_by_google_id(id_info)

    def get_by_yandex_id_or_create(
        self, id_info: Mapping[str, Any]
    ) -> UserResponse:
        return self.user_service.get_or_create_by_yandex_id(id_info)

    def get_by_email(self, email: str) -> UserResponse:
        user = self.user_service.get_by_email(email)
        return user

    def update(self, user_update: UserUpdate) -> UserResponse:
        return self.user_service.update(user_update)


def user_viewmodel_dependency(
    user_service: UserService = Depends(user_service_dependency),
) -> Generator[UserViewModel, None, None]:
    vm = UserViewModel(user_service)
    yield vm


def get_user_viewmodel() -> UserViewModel:
    return UserViewModel(get_user_service())

