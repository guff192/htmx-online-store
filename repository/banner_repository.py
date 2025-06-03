from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from db.session import db_dependency, get_db
from db_models.banner import BannerDbModel


class BannerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[BannerDbModel]:
        return self.db.query(BannerDbModel).all()


def banner_repository_dependency(
    db: Session = Depends(db_dependency),
) -> Generator[BannerRepository, None, None]:
    repo = BannerRepository(db)
    yield repo


def get_banner_repository(db: Session = get_db()) -> BannerRepository:
    return BannerRepository(db)
