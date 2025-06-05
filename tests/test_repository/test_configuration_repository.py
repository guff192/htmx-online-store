from fastapi import HTTPException
from loguru import logger
from pytest import fixture, raises
from sqlalchemy.orm import Session

from db_models.manufacturer import ManufacturerDbModel
from db_models.product import (
    AvailableProductConfigurationDbModel,
    ProductDbModel,
)
from db_models.product_configuration import (
    ConfigurationTypeDbModel,
    ProductConfigurationDbModel,
)
from exceptions.product_configurations_exceptions import ErrProductConfigurationNotFound
from repository.configuration_repository import ConfigurationRepository
from tests.fixtures.db_fixtures import db_session, engine, tables
from tests.fixtures.db_model_fixtures import (
    invalid_test_config,  # noqa F401
    invalid_test_product,  # noqa F401
    valid_test_config,  # noqa F401
    valid_test_config_type,  # noqa F401
    valid_test_configs,  # noqa F401
    valid_test_manufacturer,  # noqa F401
    valid_test_product,  # noqa F401
)
from tests.fixtures.logging_fixtures import setup_logger
from tests.fixtures.repository_fixtures import configuration_repo  # noqa F401
from tests.helpers.db_helpers import add_all_to_db, add_to_db  # noqa F401
from tests.helpers.logging_helpers import log_test_info
from tests.test_repository import log_repository_test_info


class TestGetById:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ConfigurationRepository.get_by_id() method")

    def test_with_valid_config(
        self,
        configuration_repo: ConfigurationRepository,  # noqa F811
        valid_test_config: ProductConfigurationDbModel,  # noqa F811
    ):
        logger.info("Testing with valid config")

        id_to_search = int(str(valid_test_config.id))
        found_config = configuration_repo.get_by_id(id_to_search)

        assert found_config is not None

        found_config_id = int(str(found_config.id))
        assert found_config_id == id_to_search

    def test_with_invalid_config(
        self,
        configuration_repo: ConfigurationRepository,  # noqa F811
        invalid_test_config: ProductConfigurationDbModel,  # noqa F811
    ):
        logger.info("Testing with invalid config")

        id_to_search = int(str(invalid_test_config.id))

        with raises(HTTPException) as raises_context:
            found_config = configuration_repo.get_by_id(id_to_search)

        assert raises_context.type is ErrProductConfigurationNotFound, (
            f"Expected ErrProductConfigurationNotFound, got {raises_context.type}"
        )

    def test_with_invalid_id(
        self,
        configuration_repo: ConfigurationRepository,  # noqa F811
        valid_test_config: ProductConfigurationDbModel,  # noqa F811
    ):
        logger.info("Testing with invalid id")

        id_to_search = int(str(valid_test_config.id)) + 1

        with raises(HTTPException) as raises_context:
            found_config = configuration_repo.get_by_id(id_to_search)

        assert raises_context.type is ErrProductConfigurationNotFound, (
            f"Expected ErrProductConfigurationNotFound, got {raises_context.type}"
        )

    def test_without_config(
        self,
        configuration_repo: ConfigurationRepository,  # noqa F811
    ):
        logger.info("Testing without config")

        id_to_search = 1

        with raises(HTTPException) as raises_context:
            found_config = configuration_repo.get_by_id(id_to_search)

        assert raises_context.type is ErrProductConfigurationNotFound, (
            f"Expected ErrProductConfigurationNotFound, got {raises_context.type}"
        )


class TestGetConfigurationsForProduct:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info(
            "Testing ConfigurationRepository.get_configurations_for_product() method"
        )

    def test_with_valid_product(
        self,
        configuration_repo: ConfigurationRepository,  # noqa F811
        valid_test_product: ProductDbModel,  # noqa F811
    ):
        logger.info("Testing with valid product")

        product_id = int(str(valid_test_product._id))
        orm_available_product_configurations = (
            valid_test_product.available_configurations
        )
        assert orm_available_product_configurations is not None, (
            f"Setup err: No available configurations for product {product_id}"
        )
        assert len(orm_available_product_configurations) > 0, (
            f"Setup err: No available configurations for product {product_id}"
        )

        found_configs = configuration_repo.get_configurations_for_product(product_id)
        assert len(found_configs) > 0, "No configurations found"

        for found_config in found_configs:
            assert any(
                orm_product_config.configuration_id == found_config.id
                and orm_product_config.configuration.value == found_config.value
                for orm_product_config in orm_available_product_configurations
            ), f"Config {found_config.id} not found in available configurations"
