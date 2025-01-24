from loguru import logger
from pytest import fixture
from sqlalchemy.orm import Session

from models.product import Product, ProductConfiguration, AvailableProductConfiguration
from models.manufacturer import Manufacturer
from repository.configuration_repository import ConfigurationRepository

from tests.fixtures.db_fixtures import db
from tests.fixtures.model_fixtures import (
    basic_configs,
    valid_test_config,
    valid_test_product,
    invalid_test_product,
    valid_test_manufacturer,
)
from tests.fixtures.repository_fixtures import configuration_repo
from tests.helpers.db_helpers import add_all_to_db, add_to_db


# Fixtures
@fixture(scope="function", autouse=True)
def test_cleanup(db: Session):  # noqa
    yield

    try:
        db.query(ProductConfiguration).filter(ProductConfiguration.id < 0).delete()
        db.query(AvailableProductConfiguration).delete()
        db.query(Product).delete()
        db.query(Manufacturer).delete()
        db.commit()
    except Exception as e:
        db.rollback()

        logger.error(f"Failed to cleanup test data: {str(e)}")
        raise e


# Tests
def test_pre_cleanup():
    logger.info("\n" * 2 + "=" * 50)
    logger.info("Testing Configuration Repository\n" + "=" * 50)


class TestGetById:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        logger.info("\n" * 2 + "=" * 50)
        logger.info("Testing ConfigurationRepository.get_by_id() method\n" + "=" * 50)

    def test_with_valid_config(
        self,
        configuration_repo: ConfigurationRepository,  # noqa
        valid_test_config: ProductConfiguration,  # noqa
    ):
        config = configuration_repo.get_by_id(valid_test_config.id)
        assert config is not None
        assert config.id == valid_test_config.id


class TestGetConfigurationsForProduct:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        logger.info("\n" * 2 + "=" * 50)
        logger.info("Testing ConfigurationRepository.get_by_id() method\n" + "=" * 50)

    def test_with_valid_product(
        self,
        configuration_repo: ConfigurationRepository,  # noqa
        valid_test_product: Product,  # noqa
    ):
        configs = configuration_repo.get_configurations_for_product(
            valid_test_product._id
        )
        assert len(configs) > 0
        for config in configs:
            assert config.soldered_ram == valid_test_product.soldered_ram
            assert config.additional_ram == valid_test_product.can_add_ram

    def test_with_invalid_product(
        self,
        configuration_repo: ConfigurationRepository,  # noqa
        invalid_test_product: Product,  # noqa
    ):
        configs = configuration_repo.get_configurations_for_product(
            invalid_test_product._id
        )
        assert len(configs) == 0

