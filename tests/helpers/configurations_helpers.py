from sqlalchemy import and_
from sqlalchemy.orm import Session

from db_models.product import ProductDbModel, AvailableProductConfigurationDbModel
from db_models.product_configuration import ProductConfigurationDbModel
from tests.helpers.db_helpers import add_all_to_db


def create_available_configs_for_product(db_session: Session, product: ProductDbModel, configurations: list[ProductConfigurationDbModel]):
    available_configs: list[AvailableProductConfigurationDbModel] = []
    for config in configurations:
        available_configuration = AvailableProductConfigurationDbModel(
            product_id=product._id,
            configuration_id=config.id
        )
        available_configs.append(available_configuration)
    add_all_to_db(db_session, available_configs)

    return available_configs


def get_product_configs_for_ram(db_session: Session, soldered_ram: int, can_add_ram: bool) -> list[ProductConfigurationDbModel]:
    return db_session.query(ProductConfigurationDbModel).where(and_(
        ProductConfigurationDbModel.additional_ram == can_add_ram,
        ProductConfigurationDbModel.soldered_ram == soldered_ram
    )).all()


