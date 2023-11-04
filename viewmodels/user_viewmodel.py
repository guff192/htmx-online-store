from typing import Any, Mapping

from fastapi import Depends, HTTPException
from loguru import logger

from schema.user_schema import UserBase, UserCreateGoogle
from services.auth_service import (
    GoogleOAuthService,
    get_oauth_service,
    google_oauth_service_dependency,
)
from services.user_service import UserService, get_user_service, user_service_dependency


class UserViewModel:
    def __init__(self, user_service: UserService, auth_service: GoogleOAuthService):
        self.user_service = user_service
        self.auth_service = auth_service

    def _parse_user_create_google_schema(self, google_user_id_info: Mapping[str, Any]) -> UserCreateGoogle | None:
        try:
            user_schema = UserCreateGoogle(
                google_id=str(google_user_id_info.get('sub', None)),
                name=str(google_user_id_info.get('name', '')),
                profile_img_url=str(google_user_id_info.get('picture')),
                email=str(google_user_id_info.get('email', False)),
                email_verified=bool(google_user_id_info.get('email_verified', False)),
                hd=str(google_user_id_info.get('hd', '')),
            )

            return user_schema
        except Exception as e:
            logger.debug(f'Error parsing user schema: {e}')
            return None
    
    def get_by_google_id_or_create(
        self,
        google_user_id_info: Mapping[str, Any]
    ) -> UserBase:
        user_schema = self._parse_user_create_google_schema(google_user_id_info)
        if not user_schema:
            raise HTTPException(status_code=401, detail='Invalid Google ID')
            # TODO: Change this to custom exception

        user = self.user_service.get_by_google_id_or_create(user_schema)
        return user


def user_viewmodel_dependency(
    user_service: UserService = Depends(user_service_dependency),
    auth_service: GoogleOAuthService = Depends(google_oauth_service_dependency)
):
    vm = UserViewModel(user_service, auth_service)
    yield vm


def get_user_viewmodel() -> UserViewModel:
    return UserViewModel(get_user_service(), get_oauth_service())

