from loguru import logger
from pytest import fixture
from sqlalchemy.orm import Session

from db_models.product import ProductDbModel, ProductConfigurationDbModel, AvailableProductConfigurationDbModel
from db_models.manufacturer import ManufacturerDbModel
from repository.configuration_repository import ConfigurationRepository

from tests.test_repository import log_repository_test_info

from tests.fixtures.db_fixtures import db
from tests.fixtures.model_fixtures import (
    basic_configs, # noqa F401
    valid_test_config,
    valid_test_product, # noqa F401
    invalid_test_product,
    valid_test_manufacturer,
)
from tests.fixtures.repository_fixtures import configuration_repo
from tests.helpers.db_helpers import add_all_to_db, add_to_db
from tests.helpers.logging_helpers import log_test_info


# Fixtures
@fixture(scope="function", autouse=True)
def test_cleanup(db: Session):  # noqa
    yield

    try:
        db.query(ProductConfigurationDbModel).filter(ProductConfigurationDbModel.id < 0).delete()
        db.query(AvailableProductConfigurationDbModel).delete()
        db.query(ProductDbModel).delete()
        db.query(ManufacturerDbModel).delete()
        db.commit()
    except Exception as e:
        db.rollback()

        logger.error(f"Failed to cleanup test data: {str(e)}")
        raise e


# Tests
def test_pre_cleanup():
    log_test_info("Testing Configuration Repository", level=2)


class TestGetById:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ConfigurationRepository.get_by_id() method")

    def test_with_valid_config(
        self,
        configuration_repo: ConfigurationRepository,  # noqa
        valid_test_config: ProductConfigurationDbModel,  # noqa
    ):
        id_to_search = int(str(valid_test_config.id))
        config = configuration_repo.get_by_id(id_to_search)

        assert config is not None

        found_config_id = int(str(config.id))
        assert found_config_id == id_to_search


class TestGetConfigurationsForProduct:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ConfigurationRepository.get_configurations_for_product() method")

    def test_with_valid_product(
        self,
        configuration_repo: ConfigurationRepository,  # noqa
        valid_test_product: ProductDbModel,  # noqa
    ):
        product_id = int(str(valid_test_product._id)) if str(valid_test_product._id) else None
        assert product_id is not None

        configs = configuration_repo.get_configurations_for_product(product_id)
        assert len(configs) > 0
        for config in configs:
            assert config.soldered_ram == valid_test_product.soldered_ram
            assert config.additional_ram == valid_test_product.can_add_ram

    def test_with_invalid_product(
        self,
        configuration_repo: ConfigurationRepository,  # noqa
        invalid_test_product: ProductDbModel,  # noqa
    ):
        product_id = int(str(invalid_test_product._id)) if str(invalid_test_product._id) else None
        assert product_id is not None
        configs = configuration_repo.get_configurations_for_product(product_id)
        assert len(configs) == 0
