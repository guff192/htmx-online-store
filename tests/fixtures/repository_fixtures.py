from pytest import fixture
from sqlalchemy.orm import Session

from repository.banner_repository import get_banner_repository
from repository.configuration_repository import (
    ConfigurationRepository,
    get_configuration_repository,
)
from repository.product_repository import ProductRepository, get_product_repository

from repository.user_repository import UserRepository, get_user_repository
from tests.fixtures.db_fixtures import db_session, engine, tables  # noqa


@fixture(scope="function")
def banner_repo(db_session: Session):  # noqa F811
    return get_banner_repository(db_session)


@fixture(scope="function")
def configuration_repo(db_session: Session) -> ConfigurationRepository:  # noqa F811
    return get_configuration_repository(db_session)


@fixture(scope="function")
def product_repo(
    db_session: Session, configuration_repo: ConfigurationRepository  # noqa F811
) -> ProductRepository:  # noqa F811
    return get_product_repository(db_session, configuration_repo)


@fixture(scope="function")
def user_repo(db_session: Session) -> UserRepository:  # noqa F811
    return get_user_repository(db_session)
