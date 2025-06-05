# Tests
from fastapi import HTTPException
from loguru import logger
from pytest import fixture, raises

from db_models.manufacturer import ManufacturerDbModel
from exceptions.manufacturer_exceptions import ErrManufacturerNotFound
from repository.manufacturer_repository import ManufacturerRepository, manufacturer_repository_dependency
from tests.fixtures.db_fixtures import db_session, engine, tables  # noqa F401
from tests.fixtures.db_model_fixtures.manufacturer import (
    invalid_test_manufacturer,
    valid_test_manufacturer,
    valid_test_manufacturers,  # noqa F401
)
from tests.fixtures.logging_fixtures import setup_logger  # noqa F401
from tests.fixtures.repository_fixtures import manufacturer_repo  # noqa F401
from tests.helpers.logging_helpers import log_test_info


def log_info():
    log_test_info("Testing BannerRepository methods", level=2)


class TestGetAll:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ManufacturerRepository.get_all() method")
        yield

    def test_with_valid_manufacturer(
        self,
        manufacturer_repo: ManufacturerRepository,  # noqa F811
        valid_test_manufacturer: ManufacturerDbModel,  # noqa F811
    ):
        logger.info("Testing with valid manufacturer")

        found_manufacturers = manufacturer_repo.get_all()
        assert len(found_manufacturers) == 1
        assert found_manufacturers[0].id == int(str(valid_test_manufacturer.id))
        assert found_manufacturers[0].name == str(valid_test_manufacturer.name)
        assert str(found_manufacturers[0].logo_url).strip("/") == str(
            valid_test_manufacturer.logo_url
        )

    def test_with_invalid_manufacturer(
        self,
        manufacturer_repo: ManufacturerRepository,  # noqa F811
        invalid_test_manufacturer: ManufacturerDbModel,  # noqa F811
    ):
        logger.info("Testing with invalid manufacturer")

        found_manufacturers = manufacturer_repo.get_all()
        assert len(found_manufacturers) == 0

    def test_with_multiple_valid_manufacturers(
        self,
        manufacturer_repo: ManufacturerRepository,  # noqa F811
        valid_test_manufacturers: list[ManufacturerDbModel],  # noqa F811
    ):
        logger.info("Testing with multiple valid manufacturers")

        found_manufacturers = manufacturer_repo.get_all()
        assert len(found_manufacturers) == len(valid_test_manufacturers)

        found_manufacturers_ids = [p.id for p in found_manufacturers]
        test_manufacturers_ids = [int(str(p.id)) for p in valid_test_manufacturers]
        assert any(
            test_id in found_manufacturers_ids for test_id in test_manufacturers_ids
        )
        assert any(
            found_id in test_manufacturers_ids for found_id in found_manufacturers_ids
        )

    def test_without_manufacturers(
        self,
        manufacturer_repo: ManufacturerRepository,  # noqa F811
    ):
        logger.info("Testing without manufacturers")

        found_manufacturers = manufacturer_repo.get_all()
        assert len(found_manufacturers) == 0


class TestGetById:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ManufacturerRepository.get_by_id() method")
        yield

    def test_with_valid_manufacturer(
        self,
        manufacturer_repo: ManufacturerRepository,  # noqa F811
        valid_test_manufacturer: ManufacturerDbModel,  # noqa F811
    ):
        logger.info("Testing with valid manufacturer")

        id_to_search = int(str(valid_test_manufacturer.id))
        found_manufacturer = manufacturer_repo.get_by_id(id_to_search)

        assert found_manufacturer is not None
        assert found_manufacturer.id == int(str(valid_test_manufacturer.id))
        assert found_manufacturer.name == str(valid_test_manufacturer.name)
        assert str(found_manufacturer.logo_url).strip("/") == str(
            valid_test_manufacturer.logo_url
        )

    def test_with_invalid_manufacturer(
        self,
        manufacturer_repo: ManufacturerRepository,  # noqa F811
        invalid_test_manufacturer: ManufacturerDbModel,  # noqa F811
    ):
        logger.info("Testing with invalid manufacturer")

        id_to_search = int(str(invalid_test_manufacturer.id))
        with raises(HTTPException) as raises_context:
            manufacturer_repo.get_by_id(id_to_search)

        assert raises_context.type is ErrManufacturerNotFound, (
            f"Expected ErrManufacturerNotFound, but got {raises_context.type}"
        )


class TestGetByName:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ManufacturerRepository.get_by_name() method")
        yield

    def test_with_valid_manufacturer(
        self,
        manufacturer_repo: ManufacturerRepository,  # noqa F811
        valid_test_manufacturer: ManufacturerDbModel,  # noqa F811
    ):
        logger.info("Testing with valid manufacturer")

        name_to_search = str(valid_test_manufacturer.name)
        found_manufacturer = manufacturer_repo.get_by_name(name_to_search)

        assert found_manufacturer is not None
        assert found_manufacturer.id == int(str(valid_test_manufacturer.id))
        assert found_manufacturer.name == str(valid_test_manufacturer.name)
        assert str(found_manufacturer.logo_url).strip("/") == str(
            valid_test_manufacturer.logo_url
        )

    def test_with_invalid_manufacturer(
        self,
        manufacturer_repo: ManufacturerRepository,  # noqa F811
        invalid_test_manufacturer: ManufacturerDbModel,  # noqa F811
    ):
        logger.info("Testing with invalid manufacturer")

        name_to_search = str(invalid_test_manufacturer.name)
        with raises(HTTPException) as raises_context:
            manufacturer_repo.get_by_name(name_to_search)

        assert raises_context.type is ErrManufacturerNotFound, (
            f"Expected ErrManufacturerNotFound, but got {raises_context.type}"
        )


class TestManufacturerRepositoryDependency:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ManufacturerRepository dependency")
        yield

    def test_manufacturer_repository_dependency(self):
        logger.info("Testing ManufacturerRepository dependency")

        repo = next(manufacturer_repository_dependency())
        assert isinstance(repo, ManufacturerRepository)
