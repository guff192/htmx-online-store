from fastapi import Depends, HTTPException, status

from models.user import User
from repository.user_repository import (
    UserRepository,
    get_user_repository,
    user_repository_dependency,
)
from schema.user_schema import UserCreateGoogle


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
       self.repo = user_repo

    def _get_by_google_id(self, google_id: str) -> User | None:
        return self.repo.get_by_google_id(google_id)

    def get_by_google_id_or_create(self, user_create: UserCreateGoogle) -> User:
        if not user_create.verify():
            # INFO: From here...
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User\'s not verified'
            )
            # TODO: Change this to custom exception
            
        user: User = self._get_by_google_id(user_create.google_id)
        if user is not None:
            return user

        user: User = self.repo.create(
            name=user_create.name,
            profile_img_url=user_create.profile_img_url,
            google_id=user_create.google_id
        )

        return user

def user_service_dependency(user_repo: UserRepository = Depends(user_repository_dependency)):
    service = UserService(user_repo)
    yield service

def get_user_service() -> UserService:
    return UserService(get_user_repository())

