from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from db.session import db_dependency
from db_models.banner import Banner


class BannerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Banner]:
        return self.db.query(Banner).all()


def banner_repository_dependency(
    db: Session = Depends(db_dependency),
) -> Generator[BannerRepository, None, None]:
    repo = BannerRepository(db)
    yield repo

