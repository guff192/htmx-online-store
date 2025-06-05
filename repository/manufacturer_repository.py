from fastapi import Depends
from pydantic import ValidationError
from sqlalchemy import Select, select
from sqlalchemy.exc import NoResultFound
from exceptions.manufacturer_exceptions import ErrManufacturerNotFound
from sqlalchemy.orm import Session
from db.session import db_dependency
from db_models.manufacturer import ManufacturerDbModel
from models.manufacturer import Manufacturer


class ManufacturerRepository:
    def __init__(self, db: Session):
        self.db = db

    def _get_manufacturer_select_query(self) -> Select[tuple[ManufacturerDbModel]]:
        return select(ManufacturerDbModel)

    def _add_manufacturer_id_to_query(
        self, stmt: Select[tuple[ManufacturerDbModel]], manufacturer_id: int
    ) -> Select[tuple[ManufacturerDbModel]]:
        return stmt.where(ManufacturerDbModel.id == manufacturer_id)

    def _add_name_to_query(
        self, stmt: Select[tuple[ManufacturerDbModel]], name: str
    ) -> Select[tuple[ManufacturerDbModel]]:
        return stmt.where(ManufacturerDbModel.name == name)

    def get_all(self) -> list[Manufacturer]:
        query = self._get_manufacturer_select_query()

        result = self.db.execute(query)
        orm_manufacturers = result.scalars().all()
        domain_model_manufacturers: list[Manufacturer] = []
        for orm_manufacturer in orm_manufacturers:
            try:
                manufacturer = Manufacturer.model_validate(orm_manufacturer)
                domain_model_manufacturers.append(manufacturer)
            except ValidationError:
                continue

        return domain_model_manufacturers

    def get_by_id(self, manufacturer_id: int) -> Manufacturer:
        query = self._get_manufacturer_select_query()
        query = self._add_manufacturer_id_to_query(query, manufacturer_id)

        result = self.db.execute(query)
        try:
            orm_manufacturer = result.scalar_one()
            return Manufacturer.model_validate(orm_manufacturer)
        except (NoResultFound, ValidationError):
            raise ErrManufacturerNotFound(manufacturer_id)

    def get_by_name(self, name: str) -> Manufacturer:
        query = self._get_manufacturer_select_query()
        query = self._add_name_to_query(query, name)

        result = self.db.execute(query)
        try:
            orm_manufacturer = result.scalar_one()
            return Manufacturer.model_validate(orm_manufacturer)
        except (NoResultFound, ValidationError):
            raise ErrManufacturerNotFound(name)


def manufacturer_repository_dependency(db: Session = Depends(db_dependency)):
    repo = ManufacturerRepository(db)
    yield repo


def get_manufacturer_repository(db: Session = Depends(db_dependency)):
    return ManufacturerRepository(db)
