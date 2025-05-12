from typing import Generator
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.session import db_dependency, get_db
from dto.configuration_dto import ConfigurationDTO
from db_models.product import AvailableProductConfigurationDbModel, ProductConfigurationDbModel


class ConfigurationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, id: int) -> ProductConfigurationDbModel:
        return self.db.query(ProductConfigurationDbModel).filter(
            ProductConfigurationDbModel.id == id
        ).first()

    def get_available_configurations(
        self,
        additional_ram: bool = False,
        soldered_ram: int = 0,
        ram_amount: int | None = None,
        ssd_amount: int | None = None
    ) -> list[ProductConfigurationDbModel]:
        filters = [ProductConfigurationDbModel.additional_ram == additional_ram, 
                   ProductConfigurationDbModel.soldered_ram == soldered_ram]

        if ram_amount is not None:
            filters.append(ProductConfigurationDbModel.ram_amount == ram_amount)
        if ssd_amount is not None:
            filters.append(ProductConfigurationDbModel.ssd_amount == ssd_amount)

        return self.db.query(ProductConfigurationDbModel).filter(*filters).all()

    def get_default_configurations(self):
        return self.db.query(ProductConfigurationDbModel).filter(
            ProductConfigurationDbModel.is_default == True  # noqa: E712
        ).all()

    def get_configurations_for_product(
        self,
        product_id: int,
        ram: list[int] = [],
        ssd: list[int] = [],
    ) -> list[ConfigurationDTO]:
        result: list[ConfigurationDTO] = []

        stmt = (
            select(ProductConfigurationDbModel.id,
                   ProductConfigurationDbModel.ram_amount,
                   ProductConfigurationDbModel.ssd_amount,
                   ProductConfigurationDbModel.additional_price,
                   ProductConfigurationDbModel.is_default,
                   ProductConfigurationDbModel.additional_ram,
                   ProductConfigurationDbModel.soldered_ram).
            join(AvailableProductConfigurationDbModel,
                 AvailableProductConfigurationDbModel.configuration_id == ProductConfigurationDbModel.id).
            filter(AvailableProductConfigurationDbModel.product_id == product_id)
        )
        if ram:
            stmt = stmt.filter(ProductConfigurationDbModel.ram_amount.in_(ram))
        if ssd:
            stmt = stmt.filter(ProductConfigurationDbModel.ssd_amount.in_(ssd))
        stmt.order_by(ProductConfigurationDbModel.additional_price)

        for row in self.db.execute(stmt).all():
            id, ram_amount, ssd_amount, additional_price, is_default, additional_ram, soldered_ram = row
            configuration_dto = ConfigurationDTO(
                id=id, ram_amount=ram_amount, ssd_amount=ssd_amount,
                additional_price=additional_price, is_default=is_default,
                additional_ram=additional_ram, soldered_ram=soldered_ram
            )

            result.append(configuration_dto)

        return result


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

