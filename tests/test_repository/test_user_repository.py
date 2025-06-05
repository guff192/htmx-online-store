from uuid import uuid4

from fastapi import HTTPException
from loguru import logger
from pytest import fixture, raises
from sqlalchemy import select
from sqlalchemy.orm import Session

from db_models.user import UserDbModel
from exceptions.auth_exceptions import ErrUserNotFound
from models.user import User
from repository.user_repository import UserRepository, user_repository_dependency
from tests.fixtures.db_fixtures import db_session, engine, tables  # noqa F401
from tests.fixtures.db_model_fixtures import valid_test_user  # noqa F401
from tests.fixtures.db_model_fixtures.user import invalid_test_user  # noqa F401
from tests.fixtures.logging_fixtures import setup_logger  # noqa F401
from tests.fixtures.model_fixtures.user import (
    test_user_model_with_basic_data,  # noqa F401
    test_user_model_with_google_id,  # noqa F401
    test_user_model_with_phone,  # noqa F401
    test_user_model_with_yandex_id,  # noqa F401
)
from tests.fixtures.repository_fixtures import user_repo  # noqa F401
from tests.helpers.logging_helpers import log_test_info


# Tests
def log_info():
    log_test_info("Testing BannerRepository methods", level=2)


class TestGetById:
    @fixture(scope="function")
    def log_info(self):
        log_test_info("Testing UserRepository.get_by_id() method")
        yield

    def test_with_valid_user(
        self,
        user_repo: UserRepository,  # noqa F811
        valid_test_user: UserDbModel,  # noqa F811
    ):
        logger.info("Testing with valid user")

        found_user = user_repo.get_by_id(str(valid_test_user.id))
        assert str(found_user.id) == str(valid_test_user.id)
        assert found_user.google_id == str(valid_test_user.google_id)
        assert found_user.name == str(valid_test_user.name)

    def test_with_invalid_user(
        self,
        user_repo: UserRepository,  # noqa F811
        invalid_test_user: UserDbModel,  # noqa F811
    ):
        logger.info("Testing with valid user")

        with raises(HTTPException) as raises_context:
            user_repo.get_by_id(str(invalid_test_user.id))

        assert raises_context.type is ErrUserNotFound, (
            f"Expected ErrUserNotFound, got {raises_context.type}"
        )

    def test_without_users(self, user_repo: UserRepository):  # noqa F811
        logger.info("Testing without users")

        id_to_search = str(uuid4())
        with raises(HTTPException) as raises_context:
            user_repo.get_by_id(id_to_search)

        assert raises_context.type is ErrUserNotFound, (
            f"Expected ErrUserNotFound, but got {raises_context.type}"
        )


class TestGetByPhone:
    @fixture(scope="function")
    def log_info(self):
        log_test_info("Testing UserRepository.get_by_phone() method")
        yield

    def test_with_valid_user(
        self,
        user_repo: UserRepository,  # noqa F811
        valid_test_user: UserDbModel,  # noqa F811
    ):
        logger.info("Testing with valid user")

        found_user = user_repo.get_by_phone(str(valid_test_user.phone))
        assert str(found_user.id) == str(valid_test_user.id)
        assert found_user.phone == str(valid_test_user.phone)

    def test_with_invalid_user(
        self,
        user_repo: UserRepository,  # noqa F811
        invalid_test_user: UserDbModel,  # noqa F811
    ):
        logger.info("Testing with invalid user")

        with raises(HTTPException) as raises_context:
            user_repo.get_by_phone(str(invalid_test_user.phone))

        assert raises_context.type is ErrUserNotFound, (
            f"Expected ErrUserNotFound, got {raises_context.type}"
        )

    def test_without_users(self, user_repo: UserRepository):  # noqa F811
        logger.info("Testing without users")

        phone_to_search = str(uuid4())
        with raises(HTTPException) as raises_context:
            user_repo.get_by_phone(phone_to_search)

        assert raises_context.type is ErrUserNotFound, (
            f"Expected ErrUserNotFound, but got {raises_context.type}"
        )


class TestGetByEmail:
    @fixture(scope="function")
    def log_info(self):
        log_test_info("Testing UserRepository.get_by_id() method")
        yield

    def test_with_valid_user(
        self,
        user_repo: UserRepository,  # noqa F811
        valid_test_user: UserDbModel,  # noqa F811
    ):
        logger.info("Testing with valid user")

        found_user = user_repo.get_by_email(str(valid_test_user.email))
        assert str(found_user.id) == str(valid_test_user.id)
        assert found_user.email == str(valid_test_user.email)

    def test_with_invalid_user(
        self,
        user_repo: UserRepository,  # noqa F811
        invalid_test_user: UserDbModel,  # noqa F811
    ):
        logger.info("Testing with valid user")

        with raises(HTTPException) as raises_context:
            user_repo.get_by_email(str(invalid_test_user.email))

        assert raises_context.type is ErrUserNotFound, (
            f"Expected ErrUserNotFound, got {raises_context.type}"
        )

    def test_without_users(self, user_repo: UserRepository):  # noqa F811
        logger.info("Testing without users")

        email_to_search = "test_email@test.com"
        with raises(HTTPException) as raises_context:
            user_repo.get_by_email(email_to_search)

        assert raises_context.type is ErrUserNotFound, (
            f"Expected ErrUserNotFound, but got {raises_context.type}"
        )


class TestGetByGoogleId:
    @fixture(scope="function")
    def log_info(self):
        log_test_info("Testing UserRepository.get_by_google_id() method")
        yield

    def test_with_valid_user(
        self,
        user_repo: UserRepository,  # noqa F811
        valid_test_user: UserDbModel,  # noqa F811
    ):
        logger.info("Testing with valid user")

        found_user = user_repo.get_by_google_id(str(valid_test_user.google_id))
        assert str(found_user.id) == str(valid_test_user.id)
        assert found_user.google_id == str(valid_test_user.google_id)

    def test_with_invalid_user(
        self,
        user_repo: UserRepository,  # noqa F811
        invalid_test_user: UserDbModel,  # noqa F811
    ):
        logger.info("Testing with valid user")

        with raises(HTTPException) as raises_context:
            user_repo.get_by_google_id(str(invalid_test_user.google_id))

        assert raises_context.type is ErrUserNotFound, (
            f"Expected ErrUserNotFound, got {raises_context.type}"
        )

    def test_without_users(self, user_repo: UserRepository):  # noqa F811
        logger.info("Testing without users")

        google_id_to_search = "test" * 5 + "1"
        with raises(HTTPException) as raises_context:
            user_repo.get_by_google_id(google_id_to_search)

        assert raises_context.type is ErrUserNotFound, (
            f"Expected ErrUserNotFound, but got {raises_context.type}"
        )


class TestGetByYandexId:
    @fixture(scope="function")
    def log_info(self):
        log_test_info("Testing UserRepository.get_by_yandex_id() method")
        yield

    def test_with_valid_user(
        self,
        user_repo: UserRepository,  # noqa F811
        valid_test_user: UserDbModel,  # noqa F811
    ):
        logger.info("Testing with valid user")

        found_user = user_repo.get_by_yandex_id(int(str(valid_test_user.yandex_id)))
        assert str(found_user.id) == str(valid_test_user.id)
        assert found_user.yandex_id == int(str(valid_test_user.yandex_id))

    def test_with_invalid_user(
        self,
        user_repo: UserRepository,  # noqa F811
        invalid_test_user: UserDbModel,  # noqa F811
    ):
        logger.info("Testing with valid user")

        with raises(HTTPException) as raises_context:
            user_repo.get_by_yandex_id(int(str(invalid_test_user.yandex_id)))

        assert raises_context.type is ErrUserNotFound, (
            f"Expected ErrUserNotFound, got {raises_context.type}"
        )

    def test_without_users(self, user_repo: UserRepository):  # noqa F811
        logger.info("Testing without users")

        yandex_id_to_search = 124532151
        with raises(HTTPException) as raises_context:
            user_repo.get_by_yandex_id(yandex_id_to_search)

        assert raises_context.type is ErrUserNotFound, (
            f"Expected ErrUserNotFound, but got {raises_context.type}"
        )


class TestCreate:
    @fixture(scope="function")
    def log_info(self):
        log_test_info("Testing UserRepository.create() method")
        yield

    def test_create_with_google_id(
        self,
        db_session: Session,  # noqa F811
        user_repo: UserRepository,  # noqa F811
        test_user_model_with_google_id: User,  # noqa F811
    ):
        logger.info("Testing creating with google id")

        created_user = user_repo.create(test_user_model_with_google_id)

        query = select(UserDbModel).filter(
            UserDbModel.id == test_user_model_with_google_id.id
        )
        found_user = db_session.execute(query).scalar_one()

        assert str(found_user.id) == str(test_user_model_with_google_id.id)
        assert str(found_user.google_id) == test_user_model_with_google_id.google_id
        assert str(found_user.name) == test_user_model_with_google_id.name
        assert str(found_user.email) == test_user_model_with_google_id.email

        assert created_user.id == test_user_model_with_google_id.id
        assert created_user.google_id == test_user_model_with_google_id.google_id
        assert created_user.name == test_user_model_with_google_id.name
        assert created_user.email == test_user_model_with_google_id.email

    def test_create_with_yandex_id(
        self,
        db_session: Session,  # noqa F811
        user_repo: UserRepository,  # noqa F811
        test_user_model_with_yandex_id: User,  # noqa F811
    ):
        logger.info("Testing creating with yandex id")

        created_user = user_repo.create(test_user_model_with_yandex_id)

        query = select(UserDbModel).filter(
            UserDbModel.id == test_user_model_with_yandex_id.id
        )
        found_user = db_session.execute(query).scalar_one()

        assert str(found_user.id) == str(test_user_model_with_yandex_id.id)
        assert str(found_user.phone) == test_user_model_with_yandex_id.phone
        assert str(found_user.name) == test_user_model_with_yandex_id.name
        assert str(found_user.email) == test_user_model_with_yandex_id.email

        assert created_user.id == test_user_model_with_yandex_id.id
        assert created_user.yandex_id == test_user_model_with_yandex_id.yandex_id
        assert created_user.name == test_user_model_with_yandex_id.name
        assert created_user.email == test_user_model_with_yandex_id.email

    def test_create_with_phone(
        self,
        db_session: Session,  # noqa F811
        user_repo: UserRepository,  # noqa F811
        test_user_model_with_phone: User,  # noqa F811
    ):
        logger.info("Testing creating with phone")

        created_user = user_repo.create(test_user_model_with_phone)

        query = select(UserDbModel).filter(
            UserDbModel.id == test_user_model_with_phone.id
        )
        found_user = db_session.execute(query).scalar_one()

        assert str(found_user.id) == str(test_user_model_with_phone.id)
        assert str(found_user.phone) == test_user_model_with_phone.phone
        assert str(found_user.name) == test_user_model_with_phone.name
        assert str(found_user.email) == test_user_model_with_phone.email

        assert created_user.id == test_user_model_with_phone.id
        assert created_user.phone == test_user_model_with_phone.phone
        assert created_user.name == test_user_model_with_phone.name
        assert created_user.email == test_user_model_with_phone.email

    def test_create_with_basic_data(
        self,
        db_session: Session,  # noqa F811
        user_repo: UserRepository,  # noqa F811
        test_user_model_with_basic_data: User,  # noqa F811
    ):
        logger.info("Testing creating with basic data")

        created_user = user_repo.create(test_user_model_with_basic_data)

        query = select(UserDbModel).filter(
            UserDbModel.id == test_user_model_with_basic_data.id
        )
        found_user = db_session.execute(query).scalar_one()

        assert str(found_user.id) == str(test_user_model_with_basic_data.id)
        assert str(found_user.name) == str(test_user_model_with_basic_data.name)
        assert str(found_user.email) == str(test_user_model_with_basic_data.email)

        assert created_user.id == test_user_model_with_basic_data.id
        assert created_user.name == test_user_model_with_basic_data.name
        assert created_user.email == test_user_model_with_basic_data.email
