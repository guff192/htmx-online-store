from typing import Any, Mapping

from fastapi import Depends
from schema.user_schema import UserBase
from services.user_service import (
    UserService,
    get_user_service,
    user_service_dependency
)


class UserViewModel:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def get_by_google_id_or_create(
        self, id_info: Mapping[str, Any]
    ) -> UserBase:
        user: UserBase = self.user_service.get_or_create_by_google_id(id_info)
        return user


def user_viewmodel_dependency(
    user_service: UserService = Depends(user_service_dependency),
):
    vm = UserViewModel(user_service)
    yield vm


def get_user_viewmodel() -> UserViewModel:
    return UserViewModel(get_user_service())

