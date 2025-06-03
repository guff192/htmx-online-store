from typing import Generator
from fastapi import Depends
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session
from db.session import db_dependency, get_db
from db_models.banner import BannerDbModel
from models.banner import Banner


class BannerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Banner]:
        query = select(BannerDbModel)

        result = self.db.execute(query)
        orm_banners = result.scalars().all()

        domain_model_banners: list[Banner] = []
        for orm_banner in orm_banners:
            try:
                domain_model_banners.append(Banner.model_validate(orm_banner))
            except ValidationError:
                continue

        return domain_model_banners


def banner_repository_dependency(
    db: Session = Depends(db_dependency),
) -> Generator[BannerRepository, None, None]:
    repo = BannerRepository(db)
    yield repo


def get_banner_repository(db: Session = get_db()) -> BannerRepository:
    return BannerRepository(db)
