from typing import Generator
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.session import db_dependency
from dto.configuration_dto import ConfigurationDTO
from models.product import AvailableProductConfiguration, ProductConfiguration


class ConfigurationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, id: int) -> ProductConfiguration:
        return self.db.query(ProductConfiguration).filter(
            ProductConfiguration.id == id
        ).first()

    def get_available_configurations(
        self,
        additional_ram: bool = False,
        soldered_ram: int = 0,
        ram_amount: int | None = None,
        ssd_amount: int | None = None
    ) -> list[ProductConfiguration]:
        filters = [ProductConfiguration.additional_ram == additional_ram, 
                   ProductConfiguration.soldered_ram == soldered_ram]

        if ram_amount is not None:
            filters.append(ProductConfiguration.ram_amount == ram_amount)
        if ssd_amount is not None:
            filters.append(ProductConfiguration.ssd_amount == ssd_amount)

        return self.db.query(ProductConfiguration).filter(*filters).all()

    def get_default_configurations(self):
        return self.db.query(ProductConfiguration).filter(
            ProductConfiguration.is_default == True  # noqa: E712
        ).all()

    def get_configurations_for_product(
        self,
        product_id: int
    ) -> list[ConfigurationDTO]:
        result: list[ConfigurationDTO] = []

        stmt = (
            select(ProductConfiguration.id,
                   ProductConfiguration.ram_amount,
                   ProductConfiguration.ssd_amount,
                   ProductConfiguration.additional_price,
                   ProductConfiguration.is_default,
                   ProductConfiguration.additional_ram,
                   ProductConfiguration.soldered_ram).
            join(AvailableProductConfiguration,
                 AvailableProductConfiguration.configuration_id == ProductConfiguration.id).
            filter(AvailableProductConfiguration.product_id == product_id).
            order_by(ProductConfiguration.additional_price)
        )

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

