from typing import Generator, Tuple
from fastapi import Depends
from loguru import logger
from pydantic import ValidationError
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from db.session import db_dependency, get_db
from dto.configuration_dto import ConfigurationDTO
from db_models.product import AvailableProductConfigurationDbModel
from db_models.product_configuration import ProductConfigurationDbModel
from exceptions.product_configurations_exceptions import ErrInvalidProductConfiguration, ErrProductConfigurationNotFound
from models.product_configuration import ProductConfiguration


class ConfigurationRepository:
    def __init__(self, db: Session):
        self.db = db

    def _basic_configurations_query(self) -> Select[Tuple[ProductConfigurationDbModel]]:
        return select(ProductConfigurationDbModel)

    def _add_available_configurations_join(
        self, stmt: Select[Tuple[ProductConfigurationDbModel]]
    ):
        return stmt.join(AvailableProductConfigurationDbModel)

    def get_by_id(self, id: int) -> ProductConfiguration:
        orm_configuration_model =  (
            self.db.query(ProductConfigurationDbModel)
            .filter(ProductConfigurationDbModel.id == id)
            .first()
        )
        if not orm_configuration_model:
            raise ErrProductConfigurationNotFound(config_id=id)

        try:
            return ProductConfiguration.model_validate(orm_configuration_model)
        except ValidationError:
            raise ErrProductConfigurationNotFound(config_id=id)

    def get_available_configurations(
        self,
        additional_ram: bool = False,
        soldered_ram: int = 0,
        ram_amount: int | None = None,
        ssd_amount: int | None = None,
    ) -> list[ProductConfigurationDbModel]:
        filters = [
            ProductConfigurationDbModel.additional_ram == additional_ram,
            ProductConfigurationDbModel.soldered_ram == soldered_ram,
        ]

        if ram_amount is not None:
            filters.append(ProductConfigurationDbModel.ram_amount == ram_amount)
        if ssd_amount is not None:
            filters.append(ProductConfigurationDbModel.ssd_amount == ssd_amount)

        return self.db.query(ProductConfigurationDbModel).filter(*filters).all()

    def get_default_configurations(self):
        return (
            self.db.query(ProductConfigurationDbModel)
            .filter(
                ProductConfigurationDbModel.is_default == True  # noqa: E712
            )
            .all()
        )

    def get_configurations_for_product(
        self,
        product_id: int,
    ) -> list[ProductConfiguration]:

        stmt = self._basic_configurations_query()
        stmt = self._add_available_configurations_join(stmt)
        stmt = stmt.where(AvailableProductConfigurationDbModel.product_id == product_id)
        stmt.order_by(ProductConfigurationDbModel.additional_price)

        result = self.db.execute(stmt)
        configurations_orm_models = result.scalars().all()

        configs = [
            ProductConfiguration.model_validate(orm_model)
            for orm_model in configurations_orm_models
        ]

        return configs


def configuration_repository_dependency(
    db: Session = Depends(db_dependency),
) -> Generator[ConfigurationRepository, None, None]:
    repo = ConfigurationRepository(db)
    try:
        yield repo
    finally:
        db.close()


def get_configuration_repository(
    db: Session = get_db(),
) -> ConfigurationRepository:
    return ConfigurationRepository(db)
