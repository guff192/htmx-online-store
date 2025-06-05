from pytest import fixture
from sqlalchemy.orm import Session

from db_models.manufacturer import ManufacturerDbModel
from tests.fixtures.db_fixtures import db_session, engine, tables  # noqa F401
from tests.helpers.db_helpers import add_all_to_db, add_to_db


@fixture(scope="function")
def valid_test_manufacturer(db_session: Session) -> ManufacturerDbModel:  # noqa
    manufacturer = ManufacturerDbModel(
        id=1, name="test manufacturer", logo_url="http://example.com"
    )
    add_to_db(db_session, manufacturer)

    return manufacturer


@fixture(scope="function")
def invalid_test_manufacturer(db_session: Session) -> ManufacturerDbModel:  # noqa
    manufacturer = ManufacturerDbModel(
        id=1, name="test manufacturer", logo_url="not a valid url"
    )
    add_to_db(db_session, manufacturer)

    return manufacturer


@fixture(scope="function")
def valid_test_manufacturers(db_session: Session) -> list[ManufacturerDbModel]:  # noqa
    manufacturers: list[ManufacturerDbModel] = []
    for i in range(1, 4):
        manufacturer = ManufacturerDbModel(
            id=i, name=f"test manufacturer {i}", logo_url="http://example.com"
        )
        manufacturers.append(manufacturer)

    add_all_to_db(db_session, manufacturers)
    return manufacturers
