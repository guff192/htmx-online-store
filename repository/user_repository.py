from uuid import UUID, uuid4
from fastapi import Depends
from loguru import logger
from sqlalchemy.orm import Session

from db.session import db_dependency, get_db
from models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> User | None:
        user_uuid = UUID(user_id)
        logger.debug(f'Getting user with user id: {user_id}')
        return self.db.query(User).get(user_uuid)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter_by(email=email).first()

    def get_by_google_id(self, google_id: str) -> User | None:
        return self.db.query(User).filter_by(google_id=google_id).first()

    def get_by_yandex_id(self, yandex_id: str) -> User | None:
        return self.db.query(User).filter_by(yandex_id=yandex_id).first()

    def create(self,
               name: str,
               email: str,
               profile_img_url: str | None,
               google_id: str | None = None,
               yandex_id: str | None = None) -> User | None:
        # Check if at least one of necessary fields is not None
        if not any((google_id, yandex_id)):
            return None

        # Create user using given data
        if google_id:
            logger.debug(f'Creating user with google_id: {google_id}')
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
            logger.debug(f'Creating user with yandex_id: {yandex_id}')
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
            return None

        return user


def user_repository_dependency(db: Session = Depends(db_dependency)):
    repo = UserRepository(db)
    yield repo


def get_user_repository() -> UserRepository:
    return UserRepository(get_db())

