from pytest import fixture
from sqlalchemy.orm import Session

from db_models.manufacturer import ManufacturerDbModel
from tests.fixtures.db_fixtures import db
from tests.helpers.db_helpers import add_to_db


@fixture(scope="function")
def valid_test_manufacturer(db: Session):  # noqa
    manufacturer = ManufacturerDbModel(
        id=1, name="test manufacturer", logo_url="http://example.com"
    )
    add_to_db(db, manufacturer)

    return manufacturer
