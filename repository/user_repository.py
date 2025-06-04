from typing import TypeVar
from uuid import UUID, uuid4
from fastapi import Depends
from loguru import logger
from pydantic import ValidationError
from sqlalchemy import Select, Update, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from db.session import db_dependency, get_db
from exceptions.auth_exceptions import ErrUserNotFound
from db_models.user import UserDbModel
from models.user import User


USER_QUERY_TYPE = TypeVar("USER_QUERY_TYPE", Select[tuple[UserDbModel]], Update)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def _get_user_select_query(self) -> Select[tuple[UserDbModel]]:
        return select(UserDbModel)

    def _get_user_update_query(self) -> Update:
        return update(UserDbModel)

    def _add_email_to_query(
        self, query: USER_QUERY_TYPE, email: str
    ) -> USER_QUERY_TYPE:
        return query.filter(UserDbModel.email == email)

    def _add_user_id_to_query(
        self, query: USER_QUERY_TYPE, user_id: str
    ) -> USER_QUERY_TYPE:
        user_uuid = UUID(user_id)
        return query.filter(UserDbModel.id == user_uuid)

    def _add_phone_to_query(
        self, query: USER_QUERY_TYPE, phone: str
    ) -> USER_QUERY_TYPE:
        return query.filter(UserDbModel.phone == phone)

    def _add_google_id_to_query(
        self, query: USER_QUERY_TYPE, google_id: str
    ) -> USER_QUERY_TYPE:
        return query.filter(UserDbModel.google_id == google_id)

    def _add_yandex_id_to_query(
        self, query: USER_QUERY_TYPE, yandex_id: int
    ) -> USER_QUERY_TYPE:
        return query.filter(UserDbModel.yandex_id == yandex_id)

    def get_by_id(self, user_id: str) -> User:
        query = self._get_user_select_query()
        query = self._add_user_id_to_query(query, user_id)
        result = self.db.execute(query)

        try:
            orm_user = result.scalar_one()
            domain_model_user = User.model_validate(orm_user)
        except (NoResultFound, ValidationError):
            raise ErrUserNotFound

        return domain_model_user

    def get_by_phone(self, phone: str) -> User:
        query = self._get_user_select_query()
        query = self._add_phone_to_query(query, phone)
        result = self.db.execute(query)

        try:
            orm_user = result.scalar_one()
            domain_model_user = User.model_validate(orm_user)
        except (NoResultFound, ValidationError):
            raise ErrUserNotFound

        return domain_model_user

    def get_by_email(self, email: str) -> User:
        query = self._get_user_select_query()
        query = self._add_email_to_query(query, email)
        result = self.db.execute(query)

        try:
            orm_user = result.scalar_one()
            domain_model_user = User.model_validate(orm_user)
        except (NoResultFound, ValidationError):
            raise ErrUserNotFound

        return domain_model_user

    def get_by_google_id(self, google_id: str) -> User:
        query = self._get_user_select_query()
        query = self._add_google_id_to_query(query, google_id)
        result = self.db.execute(query)

        try:
            orm_user = result.scalar_one()
            domain_model_user = User.model_validate(orm_user)
        except (NoResultFound, ValidationError):
            raise ErrUserNotFound

        return domain_model_user

    def get_by_yandex_id(self, yandex_id: int) -> User:
        query = self._get_user_select_query()
        query = self._add_yandex_id_to_query(query, yandex_id)
        result = self.db.execute(query)

        try:
            orm_user = result.scalar_one()
            domain_model_user = User.model_validate(orm_user)
        except (NoResultFound, ValidationError):
            raise ErrUserNotFound

        return domain_model_user

    def create(
        self,
        user_create_model: User,
    ) -> User:
        # Create user using given data
        user_create_orm_model = UserDbModel(
            id=user_create_model.id,
            email=user_create_model.email,
            name=user_create_model.name,
            profile_img_url=user_create_model.profile_img_url,
            google_id=user_create_model.google_id,
            yandex_id=user_create_model.yandex_id,
            phone=user_create_model.phone,
        )
        self.db.add(user_create_orm_model)
        self.db.commit()
        self.db.refresh(user_create_orm_model)

        return User.model_validate(user_create_orm_model)

    def update(self, user_uuid: UUID, name: str, email: str) -> UserDbModel:
        user_query = self.db.query(UserDbModel).filter(UserDbModel.id == user_uuid)
        found_user = user_query.first()
        if not found_user:
            raise ErrUserNotFound()
        logger.debug(f'{name = }\n{email = }\n')
        logger.debug(found_user.__dict__)

        user_update_dict = {
            UserDbModel.name: name,
            UserDbModel.email: email,
        }
        user_query.update(user_update_dict)

        self.db.commit()
        self.db.flush([found_user])

        updated_user = self.get_by_id(str(user_uuid))
        logger.debug(updated_user.__dict__)

        return updated_user


def user_repository_dependency(db: Session = Depends(db_dependency)):
    repo = UserRepository(db)
    yield repo


def get_user_repository(db: Session = get_db()) -> UserRepository:
    return UserRepository(db)

