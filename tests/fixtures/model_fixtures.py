from pytest import fixture
from sqlalchemy.orm import Session

from models.manufacturer import Manufacturer
from models.product import Product, ProductConfiguration

from tests.fixtures.db_fixtures import db
from tests.helpers.db_helpers import add_to_db, add_all_to_db
from tests.helpers.configurations_helpers import create_available_configs_for_product


@fixture(scope="function")
def valid_test_manufacturer(db: Session): # noqa
    manufacturer = Manufacturer(id=1, name="test", logo_url="test")
    add_to_db(db, manufacturer)

    return manufacturer


@fixture(scope="function")
def basic_configs(db: Session) -> list[ProductConfiguration]: # noqa
    return (
        db.query(ProductConfiguration)
        .filter(ProductConfiguration.is_default == True)  # noqa:E712
        .all()
    )


@fixture(scope="function")
def valid_test_config(db: Session): # noqa
    config = ProductConfiguration(
        id=-1, ram_amount=8, ssd_amount=256, additional_price=4000,
        is_default=False, additional_ram=False, soldered_ram=8
    )
    add_to_db(db, config)

    return config


@fixture(scope="function", params=[x + 1 for x in range(3)])
def valid_test_product(
    request,
    db: Session, # noqa
    valid_test_manufacturer: Manufacturer,
    basic_configs: list[ProductConfiguration],
) -> Product:
    product = Product(
        _id=request.param,
        name="test",
        description="test" * request.param,
        price=100000 - 30000 * request.param,
        count=100 - 40 * request.param,
        manufacturer=valid_test_manufacturer,
        manufacturer_id=valid_test_manufacturer.id,
        resolution="1920x1080",
        resolution_name="FullHD",
        cpu="i7-1185G7",
        gpu="test",
        touch_screen=True,
        cpu_speed="test",
        cpu_graphics="test",
        soldered_ram=0,
        can_add_ram=True,
    )
    add_to_db(db, product)

    available_configs = create_available_configs_for_product(db, product, basic_configs)

    add_all_to_db(db, [product] + available_configs)

    return product


@fixture(scope="function")
def valid_test_products(
    db: Session, # noqa
    valid_test_manufacturer: Manufacturer,
    basic_configs: list[ProductConfiguration],
) -> list[Product]:
    products = []

    for _id in range(1, 4):
        product = Product(
            _id=_id,
            name=f"Test product {_id}",
            description="test" * _id,
            price=100000 - 30000 * _id,
            count= 2 * _id,
            manufacturer=valid_test_manufacturer,
            manufacturer_id=valid_test_manufacturer.id,
            resolution="1920x1080",
            resolution_name="FullHD",
            cpu="i7-1185G7",
            gpu="test",
            touch_screen=True,
            cpu_speed="test",
            cpu_graphics="test",
            soldered_ram=0,
            can_add_ram=True,
        )
        products.append(product)
    add_all_to_db(db, products)

    for product in products:
        available_configs = create_available_configs_for_product(db, product, basic_configs)

    add_all_to_db(db, [product] + available_configs)

    return products


@fixture(scope="function", params=[x + 1 for x in range(3)])
def invalid_test_product(request, db: Session, valid_test_manufacturer: Manufacturer): # noqa
    product = Product(
        _id=request.param,
        name="test",
        description="test",
        price=request.param * -1**request.param,
        count=-1**request.param * 100 * request.param,
        manufacturer=valid_test_manufacturer,
        manufacturer_id=valid_test_manufacturer.id,
        resolution="1920x1080",
        resolution_name="FullHD",
        cpu="i7-1185G7",
        gpu="test",
        touch_screen=True,
        cpu_speed="test",
        cpu_graphics="test",
        soldered_ram=2,
        can_add_ram=True,
    )
    add_to_db(db, product)

    return product
