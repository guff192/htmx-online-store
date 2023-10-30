from fastapi import Depends
from loguru import logger
from sqlalchemy.orm import Session

from db.session import db_dependency, get_db
from models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).get(user_id)

    def get_by_google_id(self, google_id: str) -> User | None:
        return self.db.query(User).filter_by(google_id=google_id).first()

    def create(self,
               name: str,
               profile_img_url: str|None,
               google_id: str|None) -> User | None:
        if not any((google_id,)):
            return None

        if google_id:
            logger.debug(f'Creating user with google_id: {google_id}')
            user = User(
                    name=name,
                    profile_img_url=profile_img_url,
                    google_id=google_id
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

