from uuid import uuid4
from pytest import fixture
from sqlalchemy.orm import Session

from db_models.user import UserDbModel
from tests.fixtures.db_fixtures import db
from tests.helpers.db_helpers import add_to_db


@fixture(scope="function", params=[x + 1 for x in range(3)])
def valid_test_user(
    request,
    db: Session,  # noqa F811
) -> UserDbModel:
    user = UserDbModel(
        id=uuid4(),
        google_id="test" * 5 + str(request.param),
        yandex_id=124532151,
        name="test",
        email="test@test.com",
        phone='79991234567',
        profile_img_url='http://example.com/test.png',
        is_admin=True if request.param % 2 == 0 else False,
    )
    add_to_db(db, user)

    return user

@fixture(scope="function", params=[x + 1 for x in range(3)])
def invalid_test_user(
    request,
    db: Session  # noqa F811
) -> UserDbModel:
    user = UserDbModel(
        id=uuid4(),
        google_id="test" * 5 + str(request.param),
        yandex_id=124532151,
        name="test",
        email="test@test.com",
        phone='79991234567',
        profile_img_url="not a url",
        is_admin=True if request.param % 2 == 0 else False,
    )
    add_to_db(db, user)

    return user
