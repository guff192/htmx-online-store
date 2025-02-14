from loguru import logger
from pytest import fixture
from sqlalchemy import select
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
    valid_test_products_without_soldered_ram,
    valid_test_products_with_soldered_ram,
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
def test_filtering_log_info():
    log_test_info("Testing ProductRepository filtering methods", level=2)


class TestQueryFiltering:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository._add_query_filter() method")
        yield

    def test_query_with_valid_products(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
    ):
        logger.info("Testing query filter with valid product")
        stmt = select(Product)

        updated_stmt = product_repo._add_query_filter(
            stmt, valid_test_products_without_soldered_ram[0].name
        )
        all_products = db.execute(stmt).scalars().all()

        assert len(all_products) == 4
        assert all(p in all_products for p in valid_test_products_without_soldered_ram)
        assert all_products[0] is valid_test_products_without_soldered_ram[0]


class TestPriceFiltering:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository._add_price_filter() method")
        yield

    def test_price_filter_narrow(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
    ):  # noqa
        logger.info("Testing narrow price filter")
        stmt = select(Product)

        updated_stmt = product_repo._add_price_filter(stmt, 10_000, 15_000)
        all_products = db.execute(updated_stmt).scalars().all()
        assert len(all_products) == 1
        assert all_products[0] in valid_test_products_without_soldered_ram

    def test_price_filter_wide(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
    ):  # noqa
        logger.info("Testing wide price filter")
        stmt = select(Product)

        updated_stmt = product_repo._add_price_filter(stmt, 5_000, 150_000)
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == len(valid_test_products_without_soldered_ram)

        all_products_ids = [id(p) for p in all_products]
        valid_test_products_ids = [
            id(p) for p in valid_test_products_without_soldered_ram
        ]
        assert all(obj_id in all_products_ids for obj_id in valid_test_products_ids)

    def test_price_filter_invalid(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
    ):  # noqa
        logger.info("Testing invalid price filter")
        stmt = select(Product)

        updated_stmt = product_repo._add_price_filter(stmt, 50_000, 5_000)
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == 0


class TestRamFiltering:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository._add_ram_filter() method")
        yield

    def test_ram_filter_narrow(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
    ):
        logger.info("Testing narrow ram filter")
        stmt = select(Product)

        updated_stmt = product_repo._add_ram_filter(stmt, [16])
        all_products = db.execute(updated_stmt).scalars().all()
        assert len(all_products) == 4

    def test_ram_filter_wide(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
        basic_configs,
    ):
        logger.info("Testing wide ram filter")
        stmt = select(Product)

        possible_ram_amounts = set(int(c.ram_amount) for c in basic_configs)
        updated_stmt = product_repo._add_ram_filter(stmt, list(possible_ram_amounts))

        all_products = db.execute(updated_stmt).scalars().all()
        assert len(all_products) == 4

    def test_ram_filter_narrow_with_soldered_ram(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_with_soldered_ram: list[Product],  # noqa
    ):
        logger.info("Testing narrow ram filter with soldered ram")
        stmt = select(Product)

        updated_stmt = product_repo._add_ram_filter(stmt, [16])
        all_products = db.execute(updated_stmt).scalars().all()
        assert len(all_products) == 2

    def test_ram_filter_wide_with_soldered_ram(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_with_soldered_ram: list[Product],  # noqa
    ):
        logger.info("Testing wide ram filter with soldered ram")
        stmt = select(Product)

        updated_stmt = product_repo._add_ram_filter(stmt, [8, 24])
        all_products = db.execute(updated_stmt).scalars().all()
        assert len(all_products) == 4


class TestSsdFiltering:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository._add_ssd_filter() method")
        yield

    def test_ssd_filter_narrow(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
    ):
        logger.info("Testing narrow ssd filter")
        stmt = select(Product)

        updated_stmt = product_repo._add_ssd_filter(stmt, [512])
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == 4

    def test_ssd_filter_wide(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
        basic_configs,
    ):
        logger.info("Testing wide ssd filter")
        stmt = select(Product)

        possible_ssd_amounts = set(int(c.ssd_amount) for c in basic_configs)
        updated_stmt = product_repo._add_ssd_filter(stmt, list(possible_ssd_amounts))

        all_products = db.execute(updated_stmt).scalars().all()
        assert len(all_products) == 4


class TestCpuFiltering:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository._add_cpu_filter() method")
        yield
    
    def test_cpu_filter_wide(
        self,
        db: Session,
        product_repo: ProductRepository,
        valid_test_products_without_soldered_ram: list[Product],
        valid_test_products_with_soldered_ram: list[Product],
    ):
        logger.info("Testing wide cpu filter")
        stmt = select(Product)

        updated_stmt = product_repo._add_cpu_filter(stmt, ["i7", "i5"])
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == 8

    def test_cpu_filter_narrow(
        self,
        db: Session,
        product_repo: ProductRepository,
        valid_test_products_without_soldered_ram: list[Product],
        valid_test_products_with_soldered_ram: list[Product],
    ):
        logger.info("Testing narrow cpu filter")
        stmt = select(Product)

        updated_stmt = product_repo._add_cpu_filter(stmt, ["i7"])
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == 4


class TestResolutionFiltering:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository._add_resolution_filter() method")
        yield

    def test_resolution_filter_narrow(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
        valid_test_products_with_soldered_ram: list[Product],  # noqa
    ):
        logger.info("Testing narrow resolution filter")
        stmt = select(Product)

        updated_stmt = product_repo._add_resolution_filter(stmt, ["FullHD"])
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == 4

    def test_resolution_filter_wide(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
        valid_test_products_with_soldered_ram: list[Product],  # noqa
    ):
        logger.info("Testing wide resolution filter")
        stmt = select(Product)

        updated_stmt = product_repo._add_resolution_filter(stmt, ["FullHD", "HD"])
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == 8


class TestTouchscreenFiltering:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository._add_touchscreen_filter() method")
        yield

    def test_touchscreen_filter_true(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
        valid_test_products_with_soldered_ram: list[Product],  # noqa
    ):
        logger.info("Testing true touchscreen filter")
        stmt = select(Product)

        updated_stmt = product_repo._add_touchscreen_filter(stmt, [True])
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == 4

    def test_touchscreen_filter_false(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
        valid_test_products_with_soldered_ram: list[Product],  # noqa
    ):
        logger.info("Testing false touchscreen filter")
        stmt = select(Product)

        updated_stmt = product_repo._add_touchscreen_filter(stmt, [False])
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == 4

    def test_touchscreen_filter_all(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
        valid_test_products_with_soldered_ram: list[Product],  # noqa
    ):
        logger.info("Testing all touchscreen filter")
        stmt = select(Product)

        updated_stmt = product_repo._add_touchscreen_filter(stmt, [True, False])
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == 8


class TestGraphicsFiltering:
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository._add_graphics_filter() method")
        yield

    def test_graphics_filter_true(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
        valid_test_products_with_soldered_ram: list[Product],  # noqa
    ):
        logger.info("Testing true graphics filter")
        stmt = select(Product)

        updated_stmt = product_repo._add_graphics_filter(stmt, [True])
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == 4

    def test_graphics_filter_false(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
        valid_test_products_with_soldered_ram: list[Product],  # noqa
    ):
        logger.info("Testing true graphics filter")
        stmt = select(Product)

        updated_stmt = product_repo._add_graphics_filter(stmt, [False])
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == 4

    def test_graphics_filter_all(
        self,
        db: Session,  # noqa
        product_repo: ProductRepository,  # noqa
        valid_test_products_without_soldered_ram: list[Product],  # noqa
        valid_test_products_with_soldered_ram: list[Product],  # noqa
    ):
        logger.info("Testing true graphics filter")
        stmt = select(Product)

        updated_stmt = product_repo._add_graphics_filter(stmt, [True, False])
        all_products = db.execute(updated_stmt).scalars().all()

        assert len(all_products) == 8


def test_main_methods_log_info():
    log_test_info("Testing Product Repository main methods", level=2)


class TestGetAll:
    # Fixtures
    @fixture(scope="class", autouse=True)
    def log_info(self):
        log_test_info("Testing ProductRepository.get_all() method")
        yield

    @fixture(scope="function")
    def all_products(self, product_repo: ProductRepository):  # noqa
        offset = 0
        products: list[ProductDTO] = []
        while products_page := product_repo.get_all(offset=offset):
            products += products_page
            offset += 10

        return products

    @fixture(scope="function")
    def all_products_with_filters(self, product_repo: ProductRepository):
        offset = 0
        products: list[ProductDTO] = []
        
        products_page = product_repo.get_all(
            query="test",
            offset=offset,
            price_from=0,
            price_to=150_000,
            ram=[8],
            ssd=[256],
            cpu=["i7"],
            resolution=["FullHD"],
            touchscreen=[True, False],
            graphics=[True, False]
        )

        while products_page:
            products += products_page
            offset += 10
            products_page = product_repo.get_all(
                query="test",
                offset=offset,
                price_from=0,
                price_to=150_000,
                ram=[8],
                ssd=[256],
                cpu=["i7"],
                resolution=["FullHD"],
                touchscreen=[True, False],
                graphics=[True, False]
            )

        return products

    # Tests
    def test_with_valid_product(
        self,
        valid_test_product: Product,  # noqa
        all_products: list[ProductDTO],  # noqa
    ):
        logger.info("Testing with valid product")

        assert len(all_products) > 0, "No products were found"
        assert any(p.id == valid_test_product.id for p in all_products), (
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

    def test_with_multiple_filters_and_valid_products(
        self,
        valid_test_products_without_soldered_ram: list[Product],
        all_products_with_filters: list[ProductDTO],
    ):
        logger.info("Testing with multiple filters and valid products")

        # check that at least one product was found
        assert len(all_products_with_filters) > 0, "No products were found"

        # check that all products were found
        input_ids = [p.id for p in valid_test_products_without_soldered_ram]
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
