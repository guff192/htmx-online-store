from sqlalchemy import and_
from sqlalchemy.orm import Session

from db_models.product import Product, ProductConfiguration, AvailableProductConfiguration
from tests.helpers.db_helpers import add_all_to_db


def create_available_configs_for_product(db_session: Session, product: Product, configurations: list[ProductConfiguration]):
    available_configs: list[AvailableProductConfiguration] = []
    for config in configurations:
        available_configuration = AvailableProductConfiguration(
            product_id=product._id,
            configuration_id=config.id
        )
        available_configs.append(available_configuration)
    add_all_to_db(db_session, available_configs)

    return available_configs


def get_product_configs_for_ram(db_session: Session, soldered_ram: int, can_add_ram: bool) -> list[ProductConfiguration]:
    return db_session.query(ProductConfiguration).where(and_(
        ProductConfiguration.additional_ram == can_add_ram,
        ProductConfiguration.soldered_ram == soldered_ram
    )).all()


