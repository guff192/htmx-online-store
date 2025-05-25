from loguru import logger
from pytest import fixture
from sqlalchemy import select
from sqlalchemy.orm import Session

from db_models.product_configuration import ConfigurationTypeDbModel, ProductConfigurationDbModel
from models.product import Product
from db_models.product import ProductDbModel, AvailableProductConfigurationDbModel
from db_models.manufacturer import ManufacturerDbModel
from repository.product_repository import ProductRepository

from tests.fixtures.db_fixtures import db  # noqa F411
from tests.fixtures.logging_fixtures import setup_logger  # noqa F411
from tests.fixtures.db_model_fixtures import (
    valid_test_config_type,  # noqa F411
    valid_test_configs,  # noqa F411
    valid_test_product,  # noqa F411
    valid_test_products,  # noqa F411
    invalid_test_product,  # noqa F411
    valid_test_manufacturer,  # noqa F411
)
from tests.fixtures.repository_fixtures import product_repo, configuration_repo  # noqa F411
from tests.helpers.logging_helpers import log_product_short, log_test_info  # noqa F411


# Fixtures
@fixture(scope="function", autouse=True)
def test_cleanup(db: Session):  # noqa F811
    yield

    try:
        db.query(AvailableProductConfigurationDbModel).delete()
        db.query(ProductDbModel).delete()
        db.query(ProductConfigurationDbModel).delete()
        db.query(ConfigurationTypeDbModel).delete()
        db.query(ManufacturerDbModel).delete()
        db.commit()
    except Exception as e:
        db.rollback()

        logger.error(f"Failed to cleanup test data: {str(e)}")
        raise e


# Tests
def test_filtering_log_info():
    log_test_info("Testing ProductRepository filtering methods", level=2)


class TestQueryFiltering:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository._add_query_filter() method")
        yield

    def test_query_with_valid_products(
        self,
        db: Session,  # noqa F811
        product_repo: ProductRepository,  # noqa F811
        valid_test_products: list[ProductDbModel],  # noqa F811
    ):
        logger.info("Testing query filter with valid product")
        stmt = select(ProductDbModel)

        query = str(valid_test_products[0].description)
        updated_stmt = product_repo._add_query_filter(stmt, query)
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == len(valid_test_products)
        assert all(p in all_products for p in valid_test_products)
        assert all_products[0] is valid_test_products[0]


class TestPriceFiltering:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository._add_price_filter() method")
        yield

    def test_price_filter_narrow(
        self,
        db: Session,  # noqa F811
        product_repo: ProductRepository,  # noqa F811
        valid_test_products: list[ProductDbModel],  # noqa F811
    ):
        logger.info("Testing narrow price filter")
        stmt = select(ProductDbModel)

        updated_stmt = product_repo._add_price_filter(stmt, 10_000, 15_000)
        all_products = db.execute(updated_stmt).scalars().all()
        assert len(all_products) == 1
        assert all_products[0] in valid_test_products

    def test_price_filter_wide(
        self,
        db: Session,  # noqa F811
        product_repo: ProductRepository,  # noqa F811
        valid_test_products: list[ProductDbModel],  # noqa F811
    ):
        logger.info("Testing wide price filter")
        stmt = select(ProductDbModel)

        updated_stmt = product_repo._add_price_filter(stmt, 5_000, 150_000)
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == len(valid_test_products)

        all_products_ids = [id(p) for p in all_products]
        valid_test_products_ids = [
            id(p) for p in valid_test_products
        ]
        assert all(obj_id in all_products_ids for obj_id in valid_test_products_ids)

    def test_price_filter_invalid(
        self,
        db: Session,  # noqa F811
        product_repo: ProductRepository,  # noqa F811
        valid_test_products: list[ProductDbModel],  # noqa F811
    ):
        logger.info("Testing invalid price filter")
        stmt = select(ProductDbModel)

        updated_stmt = product_repo._add_price_filter(stmt, 50_000, 5_000)
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == 0


def test_main_methods_log_info():
    log_test_info("Testing Product Repository main methods", level=2)


class TestGetAll:
    # Fixtures
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository.get_all() method")
        yield

    @fixture(scope="function")
    def all_products(
        self,
        product_repo: ProductRepository,  # noqa F811
    ) -> list[Product]:
        offset = 0
        products: list[Product] = []
        while products_page := product_repo.get_all(offset=offset):
            products += products_page
            offset += 10

        return products

    @fixture(scope="function")
    def all_products_with_filters(
        self,
        product_repo: ProductRepository,  # noqa F811
    ):
        offset = 0
        products: list[Product] = []

        product_repository_get_all_params = {
            "query": "test",
            "price_from": 10_000,
            "price_to": 150_000,
        }

        while products_page := product_repo.get_all(
            offset=offset, **product_repository_get_all_params
        ):
            products += products_page
            offset += 10
            products_page = product_repo.get_all(
                offset=offset, **product_repository_get_all_params
            )

        return products

    # Tests
    def test_with_valid_product(
        self,
        valid_test_product: ProductDbModel,  # noqa F811
        all_products: list[Product],  # noqa F811
    ):
        logger.info("Testing with valid product")
        
        valid_test_product_id = int(str(valid_test_product._id))

        assert len(all_products) > 0, "No products were found"
        assert any(p.id == valid_test_product_id for p in all_products), (
            "Test product was not found"
        )

    def test_with_invalid_product(
        self,
        invalid_test_product: ProductDbModel,  # noqa F811
        all_products: list[Product],  # noqa F811
    ):
        logger.info("Testing with invalid product")

        invalid_test_product_id = int(str(invalid_test_product._id))

        for product in all_products:
            assert product.id != invalid_test_product_id, "Invalid product was found"

    def test_without_products(self, all_products: list[Product]):
        logger.info("Testing without products")
        assert len(all_products) == 0

    def test_with_multiple_filters_and_valid_products(
        self,
        valid_test_products: list[ProductDbModel],  # noqa F811
        all_products_with_filters: list[Product],
    ):
        logger.info("Testing with multiple filters and valid products")

        # check that at least one product was found
        assert len(all_products_with_filters) > 0, "No products were found"

        # check that all products were found
        input_ids = [int(str(p._id)) for p in valid_test_products]
        result_ids = [p.id for p in all_products_with_filters]
        assert all(
            any(input_id == result_id for result_id in result_ids)
            for input_id in input_ids
        )


class TestGetById:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository.get_by_id() method")
        yield

    def test_with_valid_product(
        self,
        product_repo: ProductRepository,  # noqa F811
        valid_test_product: ProductDbModel,  # noqa F811
    ):
        logger.info("Testing with valid product")
        product = product_repo.get_by_id(valid_test_product._id)
        assert product is not None, "Test product was not found"
        assert product is valid_test_product

    def test_without_products(
        self,
        product_repo: ProductRepository,  # noqa F811
    ):
        logger.info("Testing without products")
        product = product_repo.get_by_id(-1)
        assert product is None
