from pytest import fixture
from sqlalchemy.orm import Session

from db_models.product_configuration import (
    ConfigurationTypeDbModel,
    ProductConfigurationDbModel,
)
from tests.fixtures.db_fixtures import db_session, engine, tables
from tests.helpers.db_helpers import add_all_to_db, add_to_db


@fixture(scope="function")
def valid_test_config_type(db_session: Session):  # noqa F411
    config = ConfigurationTypeDbModel(
        id=0,
        name="test",
    )
    add_to_db(db_session, config)

    return config


@fixture(scope="function")
def valid_test_config(db_session: Session, valid_test_config_type: ConfigurationTypeDbModel):  # noqa
    config = ProductConfigurationDbModel(
        id=0,
        additional_price=1000,
        short_name="test",
        configuration_type_id=valid_test_config_type.id,
        configuration_type=valid_test_config_type,
        value="test value",
    )
    add_to_db(db_session, config)

    return config


@fixture(scope="function")
def invalid_test_config(db_session: Session, valid_test_config_type: ConfigurationTypeDbModel):  # noqa
    config = ProductConfigurationDbModel(
        id=0,
        additional_price=-1000,
        short_name="test",
        configuration_type_id=valid_test_config_type.id,
        configuration_type=valid_test_config_type,
        value="test value",
    )
    add_to_db(db_session, config)

    return config


@fixture(scope="function")
def valid_test_configs(
    db_session: Session, valid_test_config_type: ConfigurationTypeDbModel  # noqa F811
) -> list[ProductConfigurationDbModel]:  # noqa
    configs: list[ProductConfigurationDbModel] = []
    for i in range(1, 4):
        config = ProductConfigurationDbModel(
            id=i,
            additional_price=1000 * i,
            short_name="test" * i,
            configuration_type_id=valid_test_config_type.id,
            configuration_type=valid_test_config_type,
            value="test value" * i,
        )
        configs.append(config)
    add_all_to_db(db_session, configs)

    return configs
