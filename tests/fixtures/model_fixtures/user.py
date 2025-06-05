from uuid import uuid4

from pytest import fixture

from models.user import User


@fixture(scope="function")
def test_user_model_with_google_id() -> User:
    return User(
        id=uuid4(),
        google_id="test" * 5 + "1",
        name="test",
        email="test@test.com",
    )


@fixture(scope="function")
def test_user_model_with_yandex_id() -> User:
    return User(
        id=uuid4(),
        phone="79991234567",
        name="test",
        email="test@test.com",
    )


@fixture(scope="function")
def test_user_model_with_phone() -> User:
    return User(
        id=uuid4(),
        phone="79991234567",
        name="test",
        email="test@test.com",
    )


@fixture(scope="function")
def test_user_model_with_basic_data() -> User:
    return User(
        id=uuid4(),
        name="test",
        email="test@test.com",
    )
