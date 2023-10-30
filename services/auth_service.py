from typing import Any, Mapping

from fastapi import Depends, HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token
from loguru import logger

from app.config import Settings
from repository.user_repository import (
    UserRepository,
    get_user_repository,
    user_repository_dependency,
)

settings = Settings()


class GoogleOAuthService:
    def __init__(self, user_repo: UserRepository):
        self.repo = user_repo
    
    def verify_google_oauth2(
        self,
        credential: str, form_csrf_token: str='',
        cookie_csrf_token: str=''
    ) -> Mapping[str, Any]:
        if form_csrf_token != cookie_csrf_token:
            raise HTTPException(status_code=400, detail='Wrong CSRF token!')
            # TODO: Change this to custom exception

        try:
            # geting user info
            # google-way
            id_info: Mapping[str, Any] = id_token.verify_oauth2_token(
                credential,
                requests.Request(),
                settings.google_oauth2_client_id
            )

            return id_info
        except Exception as e:
            logger.debug(f'Failed google authentication: {e}')
            raise HTTPException(status_code=401, detail='Failed google authentication: {e}')
            # TODO: Change this to custom exception


def google_oauth_service_dependency(user_repo: UserRepository = Depends(user_repository_dependency)):
    service = GoogleOAuthService(user_repo)
    yield service


def get_oauth_service() -> GoogleOAuthService:
    return GoogleOAuthService(get_user_repository())

