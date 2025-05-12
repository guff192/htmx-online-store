from fastapi import Depends
from sqlalchemy.orm import Session
from db.session import db_dependency
from db_models.manufacturer import ManufacturerDbModel


class ManufacturerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[ManufacturerDbModel]:
        return self.db.query(ManufacturerDbModel).all()

    def get_by_id(self, manufacturer_id: int) -> ManufacturerDbModel | None:
        return self.db.query(ManufacturerDbModel).get(manufacturer_id)

    def get_by_name(self, name: str) -> ManufacturerDbModel | None:
        return self.db.query(ManufacturerDbModel).filter(
            ManufacturerDbModel.name == name
        ).first()


def manufacturer_repository_dependency(db: Session = Depends(db_dependency)):
    repo = ManufacturerRepository(db)
    yield repo

