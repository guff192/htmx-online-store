from loguru import logger
from pytest import fixture
from sqlalchemy.orm import Session

from db_models.product import (
    ProductDbModel,
    AvailableProductConfigurationDbModel,
)
from db_models.product_configuration import (
    ProductConfigurationDbModel,
    ConfigurationTypeDbModel,
)
from db_models.manufacturer import ManufacturerDbModel
from exceptions.product_configurations_exceptions import ErrProductConfigurationNotFound
from repository.configuration_repository import ConfigurationRepository

from tests.test_repository import log_repository_test_info

from tests.fixtures.db_fixtures import db
from tests.fixtures.logging_fixtures import setup_logger
from tests.fixtures.db_model_fixtures import (
    valid_test_config,  # noqa F401
    valid_test_config_type,  # noqa F401
    valid_test_configs,  # noqa F401
    valid_test_product,  # noqa F401
    invalid_test_config,  # noqa F401
    invalid_test_product,  # noqa F401
    valid_test_manufacturer,  # noqa F401
)
from tests.fixtures.repository_fixtures import configuration_repo  # noqa F401
from tests.helpers.db_helpers import add_all_to_db, add_to_db  # noqa F401
from tests.helpers.logging_helpers import log_test_info


# Fixtures
@fixture(scope="function", autouse=True)
def test_cleanup(db: Session):  # noqa F811
    yield

    try:
        db.query(AvailableProductConfigurationDbModel).delete()
        db.query(ProductDbModel).delete()
        db.query(ProductConfigurationDbModel).delete()
        db.query(ConfigurationTypeDbModel).delete()
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
        configuration_repo: ConfigurationRepository,  # noqa F811
        valid_test_config: ProductConfigurationDbModel,  # noqa F811
    ):
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

        try:
            found_config = configuration_repo.get_by_id(id_to_search)
        except Exception as e:
            assert isinstance(e, ErrProductConfigurationNotFound), (
                f"Expected ErrProductConfigurationNotFound, got {type(e)}"
            )
            return

        assert False, (
            "Expected ErrProductConfigurationNotFound, but no exception was raised"
        )

    def test_with_invalid_id(
        self,
        configuration_repo: ConfigurationRepository,  # noqa F811
        valid_test_config: ProductConfigurationDbModel,  # noqa F811
    ):
        id_to_search = int(str(valid_test_config.id)) + 1

        try:
            found_config = configuration_repo.get_by_id(id_to_search)
        except Exception as e:
            assert isinstance(e, ErrProductConfigurationNotFound), (
                f"Expected ErrProductConfigurationNotFound, got {type(e)}"
            )
            return

        assert False, (
            "Expected ErrProductConfigurationNotFound, but no exception was raised"
        )

    def test_without_config(
        self,
        configuration_repo: ConfigurationRepository,  # noqa F811
    ):
        id_to_search = 1

        try:
            found_config = configuration_repo.get_by_id(id_to_search)
        except Exception as e:
            assert isinstance(e, ErrProductConfigurationNotFound), (
                f"Expected ErrProductConfigurationNotFound, got {type(e)}"
            )
            return

        assert False, (
            "Expected ErrProductConfigurationNotFound, but no exception was raised"
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
        product_id = (
            int(str(valid_test_product._id)) if str(valid_test_product._id) else None
        )
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
        assert len(found_configs) > 0

        for found_config in found_configs:
            assert any(
                orm_product_config.configuration_id == found_config.id
                and orm_product_config.configuration.value == found_config.value
                for orm_product_config in orm_available_product_configurations
            )
