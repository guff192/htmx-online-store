from pytest import fixture
from sqlalchemy.orm import Session

from repository.configuration_repository import ConfigurationRepository, get_configuration_repository
from repository.product_repository import ProductRepository, get_product_repository

from tests.fixtures.db_fixtures import db # noqa


@fixture(scope="function")
def configuration_repo(db: Session) -> ConfigurationRepository:
    return get_configuration_repository(db)


@fixture(scope="function")
def product_repo(db: Session, configuration_repo: ConfigurationRepository) -> ProductRepository:
    return get_product_repository(db, configuration_repo)

