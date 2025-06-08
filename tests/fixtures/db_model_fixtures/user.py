from uuid import uuid4
from pytest import fixture
from sqlalchemy.orm import Session

from db_models.user import UserDbModel
from tests.fixtures.db_fixtures import db_session, engine, tables
from tests.helpers.db_helpers import add_to_db


@fixture(scope="function")
def valid_test_user(
    db_session: Session,  # noqa F811
) -> UserDbModel:
    user = UserDbModel(
        id=uuid4(),
        google_id="test",
        yandex_id=124532151,
        name="test",
        email="test@test.com",
        phone="79991234567",
        profile_img_url="http://example.com/test.png",
        is_admin=True,
    )
    add_to_db(db_session, user)

    return user


@fixture(scope="function")
def invalid_test_user(
    db_session: Session,  # noqa F811
) -> UserDbModel:
    user = UserDbModel(
        id=uuid4(),
        google_id="test",
        yandex_id=124532151,
        name="test",
        email="test@test.com",
        phone="7999123456",
        profile_img_url="not a url",
        is_admin=True,
    )
    add_to_db(db_session, user)

    return user
