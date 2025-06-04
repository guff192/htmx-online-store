from uuid import uuid4

from loguru import logger
from pytest import fixture
from sqlalchemy.orm import Session

from db_models.user import UserDbModel
from exceptions.auth_exceptions import ErrUserNotFound
from repository.user_repository import UserRepository
from tests.fixtures.db_fixtures import db  # noqa F401
from tests.fixtures.db_model_fixtures import valid_test_user  # noqa F401
from tests.fixtures.db_model_fixtures.user import invalid_test_user  # noqa F401
from tests.fixtures.repository_fixtures import user_repo  # noqa F401
from tests.helpers.logging_helpers import log_test_info


@fixture(scope="function", autouse=True)
def test_cleanup(db: Session):  # noqa F811
    yield

    try:
        db.query(UserDbModel).delete()
        db.commit()
    except Exception as e:
        db.rollback()

        logger.error(f"Failed to cleanup test data: {str(e)}")
        raise e


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

        try:
            user_repo.get_by_id(str(invalid_test_user.id))
        except Exception as e:
            assert isinstance(e, ErrUserNotFound), (
                f"Expected ErrUserNotFound, got {type(e)}"
            )
            return

        assert False, "Expected ErrUserNotFound, but no exception was raised"

    def test_without_users(self, user_repo: UserRepository):  # noqa F811
        logger.info("Testing without users")

        id_to_search = str(uuid4())
        try:
            user_repo.get_by_id(id_to_search)
        except Exception as e:
            assert isinstance(e, ErrUserNotFound), (
                f"Expected ErrUserNotFound, but got {type(e)}"
            )
            return

        assert False, "Expected ErrUserNotFound, but no exception was raised"


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

        try:
            user_repo.get_by_phone(str(invalid_test_user.phone))
        except Exception as e:
            assert isinstance(e, ErrUserNotFound), (
                f"Expected ErrUserNotFound, got {type(e)}"
            )
            return

        assert False, "Expected ErrUserNotFound, but no exception was raised"

    def test_without_users(self, user_repo: UserRepository):  # noqa F811
        logger.info("Testing without users")

        phone_to_search = str(uuid4())
        try:
            user_repo.get_by_phone(phone_to_search)
        except Exception as e:
            assert isinstance(e, ErrUserNotFound), (
                f"Expected ErrUserNotFound, but got {type(e)}"
            )
            return

        assert False, "Expected ErrUserNotFound, but no exception was raised"


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

        try:
            user_repo.get_by_email(str(invalid_test_user.email))
        except Exception as e:
            assert isinstance(e, ErrUserNotFound), (
                f"Expected ErrUserNotFound, got {type(e)}"
            )
            return

        assert False, "Expected ErrUserNotFound, but no exception was raised"

    def test_without_users(self, user_repo: UserRepository):  # noqa F811
        logger.info("Testing without users")

        email_to_search = "test_email@test.com"
        try:
            user_repo.get_by_email(email_to_search)
        except Exception as e:
            assert isinstance(e, ErrUserNotFound), (
                f"Expected ErrUserNotFound, but got {type(e)}"
            )
            return

        assert False, "Expected ErrUserNotFound, but no exception was raised"


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

        try:
            user_repo.get_by_google_id(str(invalid_test_user.google_id))
        except Exception as e:
            assert isinstance(e, ErrUserNotFound), (
                f"Expected ErrUserNotFound, got {type(e)}"
            )
            return

        assert False, "Expected ErrUserNotFound, but no exception was raised"

    def test_without_users(self, user_repo: UserRepository):  # noqa F811
        logger.info("Testing without users")

        google_id_to_search = "test" * 5 + "1"
        try:
            user_repo.get_by_google_id(google_id_to_search)
        except Exception as e:
            assert isinstance(e, ErrUserNotFound), (
                f"Expected ErrUserNotFound, but got {type(e)}"
            )
            return

        assert False, "Expected ErrUserNotFound, but no exception was raised"


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

        try:
            user_repo.get_by_yandex_id(int(str(invalid_test_user.yandex_id)))
        except Exception as e:
            assert isinstance(e, ErrUserNotFound), (
                f"Expected ErrUserNotFound, got {type(e)}"
            )
            return

        assert False, "Expected ErrUserNotFound, but no exception was raised"

    def test_without_users(self, user_repo: UserRepository):  # noqa F811
        logger.info("Testing without users")

        yandex_id_to_search = 124532151
        try:
            user_repo.get_by_yandex_id(yandex_id_to_search)
        except Exception as e:
            assert isinstance(e, ErrUserNotFound), (
                f"Expected ErrUserNotFound, but got {type(e)}"
            )
            return

        assert False, "Expected ErrUserNotFound, but no exception was raised"
