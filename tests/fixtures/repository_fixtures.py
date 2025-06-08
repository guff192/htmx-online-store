from pytest import fixture
from sqlalchemy.orm import Session

from repository.banner_repository import get_banner_repository
from repository.cart_repository import get_cart_repository
from repository.configuration_repository import (
    ConfigurationRepository,
    get_configuration_repository,
)
from repository.manufacturer_repository import (
    ManufacturerRepository,
    get_manufacturer_repository,
)
from repository.product_repository import ProductRepository, get_product_repository
from repository.user_repository import UserRepository, get_user_repository
from tests.fixtures.db_fixtures import db_session, engine, tables  # noqa


@fixture(scope="function")
def banner_repo(db_session: Session):  # noqa F811
    return get_banner_repository(db_session)


@fixture(scope="function")
def cart_repo(
    db_session: Session,  # noqa F811
    product_repo: ProductRepository,
    user_repo: UserRepository,
):
    return get_cart_repository(db_session, product_repo, user_repo)


@fixture(scope="function")
def configuration_repo(db_session: Session) -> ConfigurationRepository:  # noqa F811
    return get_configuration_repository(db_session)


@fixture(scope="function")
def manufacturer_repo(db_session: Session) -> ManufacturerRepository:  # noqa F811
    return get_manufacturer_repository(db_session)


@fixture(scope="function")
def product_repo(
    db_session: Session,  # noqa F811
    configuration_repo: ConfigurationRepository,  # noqa F811
) -> ProductRepository:  # noqa F811
    return get_product_repository(db_session, configuration_repo)


@fixture(scope="function")
def user_repo(db_session: Session) -> UserRepository:  # noqa F811
    return get_user_repository(db_session)
