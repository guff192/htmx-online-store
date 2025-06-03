from pytest import fixture
from sqlalchemy.orm import Session

from db_models.banner import BannerDbModel
from tests.fixtures.db_fixtures import db  # noqa F401
from tests.helpers.db_helpers import add_all_to_db, add_to_db


@fixture(scope="function")
def valid_test_banner(db: Session):  # noqa F811
    banner = BannerDbModel(
        _id=1,
        name="test",
        description="test banner",
        img_url="http://example.com",
    )
    add_to_db(db, banner)

    return banner


@fixture(scope="function")
def invalid_test_banner(db: Session):  # noqa F811
    banner = BannerDbModel(
        _id=1,
        name="test",
        description="test banner",
        img_url="not a url",
    )
    add_to_db(db, banner)

    return banner


@fixture(scope="function")
def valid_test_banners(db: Session):  # noqa F811
    banners: list[BannerDbModel] = []
    for i in range(1, 4):
        banners.append(
            BannerDbModel(
                _id=i,
                name=f"test{i}",
                description=f"test banner {i}",
                img_url=f"http://example.com/{i}",
            )
        )

    add_all_to_db(db, banners)

    return banners
