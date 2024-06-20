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

    def get_configurations_by_names(
        self,
        names: list[str]
    ) -> list[ProductConfiguration]:
        return self.db.query(ProductConfiguration).filter(
            ProductConfiguration.name.in_(names)
        ).all()

    def get_default_configurations(self):
        return self.db.query(ProductConfiguration).filter(
            ProductConfiguration.is_default == True
        ).all()

    def get_configurations_for_product(
        self,
        product_id: int
    ) -> list[ConfigurationDTO]:
        result: list[ConfigurationDTO] = []

        stmt = (
            select(ProductConfiguration.id,
                   ProductConfiguration.name,
                   ProductConfiguration.additional_price).
            join(AvailableProductConfiguration,
                 AvailableProductConfiguration.configuration_id == ProductConfiguration.id).
            filter(AvailableProductConfiguration.product_id == product_id).
            order_by(ProductConfiguration.additional_price)
        )

        for row in self.db.execute(stmt).all():
            id, name, price = row
            configuration_dto = ConfigurationDTO(
                id=id, name=name, additional_price=price
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

