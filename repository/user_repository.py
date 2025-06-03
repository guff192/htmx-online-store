from uuid import UUID, uuid4
from fastapi import Depends
from loguru import logger
from sqlalchemy.orm import Session

from db.session import db_dependency, get_db
from exceptions.auth_exceptions import ErrUserNotFound
from db_models.user import UserDbModel


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> UserDbModel | None:
        user_uuid = UUID(user_id)
        return self.db.query(UserDbModel).get(user_uuid)

    def get_by_phone(self, phone: str) -> UserDbModel | None:
        return self.db.query(UserDbModel).filter_by(phone=phone).first()

    def get_by_email(self, email: str) -> UserDbModel | None:
        return self.db.query(UserDbModel).filter_by(email=email).first()

    def get_by_google_id(self, google_id: str) -> UserDbModel | None:
        return self.db.query(UserDbModel).filter_by(google_id=google_id).first()

    def get_by_yandex_id(self, yandex_id: int) -> UserDbModel | None:
        return self.db.query(UserDbModel).filter_by(yandex_id=yandex_id).first()

    def create(self,
               name: str,
               email: str,
               profile_img_url: str = '',
               google_id: str | None = None,
               yandex_id: int | None = None,
               phone: str | None = None) -> UserDbModel:
        # Create user using given data
        if google_id:
            user = UserDbModel(
                id=uuid4(),
                email=email,
                name=name,
                profile_img_url=profile_img_url,
                google_id=google_id,
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        elif yandex_id:
            user = UserDbModel(
                id=uuid4(),
                email=email,
                name=name,
                profile_img_url=profile_img_url,
                yandex_id=yandex_id
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        elif phone:
            user = UserDbModel(
                id=uuid4(),
                email=email,
                name=name,
                phone=phone
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        else:
            user = UserDbModel(
                id=uuid4(),
                email=email,
                name=name
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        return user

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

