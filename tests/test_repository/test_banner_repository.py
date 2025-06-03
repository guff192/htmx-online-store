# Fixtures
from loguru import logger
from pytest import fixture
from sqlalchemy.orm import Session

from db_models.banner import BannerDbModel
from repository.banner_repository import BannerRepository, banner_repository_dependency
from tests.fixtures.db_fixtures import db  # noqa F401
from tests.fixtures.db_model_fixtures import (  # noqa F401
    invalid_test_banner,
    valid_test_banner,
    valid_test_banners,
)
from tests.fixtures.repository_fixtures import banner_repo  # noqa F401
from tests.helpers.logging_helpers import log_test_info


@fixture(scope="function", autouse=True)
def test_cleanup(db: Session):  # noqa F811
    yield

    try:
        db.query(BannerDbModel).delete()
        db.commit()
    except Exception as e:
        db.rollback()

        logger.error(f"Failed to cleanup test data: {str(e)}")
        raise e


# Tests
def log_info():
    log_test_info("Testing BannerRepository methods", level=2)


class TestGetAll:
    @fixture(scope="class")
    def log_info(self):
        log_test_info("Testing BannerRepository.get_all() method")
        yield

    def test_with_valid_banners(
        self,
        banner_repo: BannerRepository,  # noqa F811
        valid_test_banners: list[BannerDbModel],  # noqa F811
    ):
        logger.info("Testing get_all with valid banner")
        found_banners = banner_repo.get_all()

        assert len(found_banners) == len(valid_test_banners)

        found_banners_ids = (b.id for b in found_banners)
        test_banners_ids = (b._id for b in valid_test_banners)
        assert all(int(str(test_id)) in found_banners_ids for test_id in test_banners_ids)

    def test_with_single_valid_banner(
        self,
        banner_repo: BannerRepository,  # noqa F811
        valid_test_banner: BannerDbModel,  # noqa F811
    ):
        logger.info("Testing get_all with single valid banner")
        found_banners = banner_repo.get_all()
        logger.debug(f"{found_banners = }")

        assert len(found_banners) == 1

        found_banner = found_banners[0]
        logger.debug(f"{found_banner = }")
        assert found_banner.name == str(valid_test_banner.name)

    def test_with_invalid_banner(
        self,
        banner_repo: BannerRepository,  # noqa F811
        invalid_test_banner: BannerDbModel,  # noqa F811
    ):
        logger.info("Testing get_all with invalid banner")

        found_banners = banner_repo.get_all()
        assert len(found_banners) == 0

    def test_without_banners(
        self,
        banner_repo: BannerRepository,  # noqa F811
    ):
        logger.info("Testing get_all without banners")

        found_banners = banner_repo.get_all()
        assert len(found_banners) == 0


class TestBannerRepositoryDependency:
    @fixture(scope="function")
    def log_info(self):
        log_test_info("Testing BannerRepository dependency")
        yield

    def test_banner_repository_dependency(self):  # noqa F811
        repo = next(banner_repository_dependency())
        assert isinstance(repo, BannerRepository)
