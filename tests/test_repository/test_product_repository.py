from loguru import logger
from pytest import fixture
from sqlalchemy.orm import Session

from dto.product_dto import ProductDTO
from models.product import Product, AvailableProductConfiguration
from models.manufacturer import Manufacturer
from repository.product_repository import ProductRepository

from tests.fixtures.db_fixtures import db
from tests.fixtures.logging_fixtures import setup_logger
from tests.fixtures.model_fixtures import (
    basic_configs,
    valid_test_product,
    valid_test_products,
    invalid_test_product,
    valid_test_manufacturer,
    valid_test_config,
)
from tests.fixtures.repository_fixtures import product_repo, configuration_repo
from tests.helpers.logging_helpers import log_product_short, log_test_info


# Fixtures
@fixture(scope="function", autouse=True)
def test_cleanup(db: Session):  # noqa
    yield

    try:
        db.query(AvailableProductConfiguration).delete()
        db.query(Product).delete()
        db.query(Manufacturer).delete()
        db.commit()
    except Exception as e:
        db.rollback()

        logger.error(f"Failed to cleanup test data: {str(e)}")
        raise e


# Tests
def test_pre_cleanup():
    log_test_info("Testing Product Repository", level=2)


class TestFiltering:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository filtering methods")
        yield

    def test_query_with_valid_product(
        self, db: Session, product_repo: ProductRepository, valid_test_products: list[Product]  # noqa
    ):
        logger.info("Testing query filter")
        stmt = db.query(Product)

        updated_stmt = product_repo._add_query_filter(stmt, valid_test_products[0].name)
        all_products = updated_stmt.all()
        assert len(all_products) == 1
        assert all_products[0] is valid_test_products[0]


class TestGetAll:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository.get_all() method")
        yield

    @fixture(scope="function")
    def all_products(self, product_repo: ProductRepository):  # noqa
        offset = 0
        products: list[ProductDTO] = []
        while products_page := product_repo.get_all(offset=offset):
            products.extend(products_page)
            offset += 10

        return products

    def test_with_valid_product(
        self,
        valid_test_product: Product,  # noqa
        all_products: list[ProductDTO],  # noqa
    ):
        logger.info("Testing with valid product")
        assert len(all_products) > 0, "No products were found"
        assert any(p.id == valid_test_product._id for p in all_products), (
            "Test product was not found"
        )

    def test_with_invalid_product(
        self,
        invalid_test_product: Product,  # noqa
        all_products: list[ProductDTO],  # noqa
    ):
        logger.info("Testing with invalid product")

        for product in all_products:
            assert product.id != invalid_test_product._id, "Invalid product was found"

    def test_without_products(self, all_products: list[ProductDTO]):
        logger.info("Testing without products")
        assert len(all_products) == 0


class TestGetById:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository.get_by_id() method")
        yield

    def test_with_valid_product(
        self,
        product_repo: ProductRepository,  # noqa
        valid_test_product: Product,  # noqa
    ):
        logger.info("Testing with valid product")
        product = product_repo.get_by_id(valid_test_product._id)
        assert product is not None, "Test product was not found"
        assert product is valid_test_product

    def test_without_products(self, product_repo: ProductRepository):  # noqa
        logger.info("Testing without products")
        product = product_repo.get_by_id(-1)
        assert product is None
