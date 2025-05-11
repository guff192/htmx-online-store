from fastapi import Depends
from sqlalchemy.orm import Session
from db.session import db_dependency
from db_models.manufacturer import Manufacturer


class ManufacturerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Manufacturer]:
        return self.db.query(Manufacturer).all()

    def get_by_id(self, manufacturer_id: int) -> Manufacturer | None:
        return self.db.query(Manufacturer).get(manufacturer_id)

    def get_by_name(self, name: str) -> Manufacturer | None:
        return self.db.query(Manufacturer).filter(
            Manufacturer.name == name
        ).first()


def manufacturer_repository_dependency(db: Session = Depends(db_dependency)):
    repo = ManufacturerRepository(db)
    yield repo

