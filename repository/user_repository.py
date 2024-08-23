from uuid import UUID, uuid4
from fastapi import Depends
from loguru import logger
from sqlalchemy.orm import Session

from db.session import db_dependency, get_db
from exceptions.auth_exceptions import ErrUserNotFound
from models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> User | None:
        user_uuid = UUID(user_id)
        return self.db.query(User).get(user_uuid)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter_by(email=email).first()

    def get_by_google_id(self, google_id: str) -> User | None:
        return self.db.query(User).filter_by(google_id=google_id).first()

    def get_by_yandex_id(self, yandex_id: int) -> User | None:
        return self.db.query(User).filter_by(yandex_id=yandex_id).first()

    def create(self,
               name: str,
               email: str,
               profile_img_url: str = '',
               google_id: str | None = None,
               yandex_id: int | None = None) -> User:
        # Create user using given data
        if google_id:
            user = User(
                id=uuid4(),
                email=email,
                name=name,
                profile_img_url=profile_img_url,
                google_id=google_id
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        elif yandex_id:
            user = User(
                id=uuid4(),
                email=email,
                name=name,
                profile_img_url=profile_img_url,
                yandex_id=yandex_id
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        else:
            user = User(
                id=uuid4(),
                email=email,
                name=name
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        return user

    def update(self, user_uuid: UUID, name: str, email: str) -> User:
        user_query = self.db.query(User).filter(User.id == user_uuid)
        found_user = user_query.first()
        if not found_user:
            raise ErrUserNotFound()
        logger.debug(f'{name = }\n{email = }\n')
        logger.debug(found_user.__dict__)

        user_update_dict = {
            User.name: name,
            User.email: email,
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


def get_user_repository() -> UserRepository:
    return UserRepository(get_db())

