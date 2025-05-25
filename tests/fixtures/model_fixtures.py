from pytest import fixture
from sqlalchemy.orm import Session

from db_models.manufacturer import ManufacturerDbModel
from db_models.product import ProductDbModel
from db_models.product_configuration import (
    ConfigurationTypeDbModel,
    ProductConfigurationDbModel,
)

from tests.helpers.db_helpers import add_to_db, add_all_to_db
from tests.helpers.configurations_helpers import create_available_configs_for_product, get_product_configs_for_ram


@fixture(scope="function")
def valid_test_manufacturer(db: Session):  # noqa
    manufacturer = ManufacturerDbModel(
        id=1, name="test manufacturer", logo_url="http://example.com"
    )
    add_to_db(db, manufacturer)

    return manufacturer


@fixture(scope="function")
def valid_test_config_type(db: Session):  # noqa F411
    config = ConfigurationTypeDbModel(
        id=0,
        name="test",
    )
    add_to_db(db, config)

    return config


@fixture(scope="function")
def valid_test_config(db: Session, valid_test_config_type: ConfigurationTypeDbModel):  # noqa
    config = ProductConfigurationDbModel(
        id=0,
        additional_price=1000,
        short_name="test",
        configuration_type_id=valid_test_config_type.id,
        configuration_type=valid_test_config_type,
        value="test value",
    )
    add_to_db(db, config)

    return config


@fixture(scope="function")
def valid_test_configs(
    db: Session, valid_test_config_type: ConfigurationTypeDbModel
) -> list[ProductConfigurationDbModel]:  # noqa
    configs: list[ProductConfigurationDbModel] = []
    for i in range(1, 4):
        config = ProductConfigurationDbModel(
            id=i,
            additional_price=1000 * i,
            short_name="test" * i,
            configuration_type_id=valid_test_config_type.id,
            configuration_type=valid_test_config_type,
            value="test value" * i,
        )
        configs.append(config)
    add_all_to_db(db, configs)

    return configs


@fixture(scope="function", params=[x + 1 for x in range(3)])
def valid_test_product(
    request,
    db: Session,  # noqa
    valid_test_manufacturer: ManufacturerDbModel,
    basic_configs: list[ProductConfigurationDbModel],
) -> ProductDbModel:
    product = ProductDbModel(
        _id=request.param,
        name="test",
        description="test" * request.param,
        price=100000 - 30000 * request.param,
        count=100 - 30 * request.param,
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


@fixture(scope="function", params=[x + 1 for x in range(3)])
def invalid_test_product(request, db: Session, valid_test_manufacturer: ManufacturerDbModel):  # noqa
    product = ProductDbModel(
        _id=request.param,
        name=f"test {request.param}",
        description="test",
        price=request.param * (-1**request.param),
        count=(-1**request.param) * 100 * request.param,
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
        can_add_ram=False,
    )
    add_to_db(db, product)

    product_configs = get_product_configs_for_ram(db, product.soldered_ram, product.can_add_ram)
    available_configs = create_available_configs_for_product(db, product, product_configs)

    add_all_to_db(db, [product] + available_configs)

    return product


@fixture(scope="function")
def valid_test_products_without_soldered_ram(
    db: Session,  # noqa
    valid_test_manufacturer: ManufacturerDbModel,
    basic_configs: list[ProductConfigurationDbModel],
) -> list[ProductDbModel]:
    products = []
    for _id in range(0, 4):
        product = ProductDbModel(
            _id=_id,
            name=f"Test product {_id}",
            description="test" * _id,
            price=100_000 - 30_000 * _id,
            count=2 * _id,
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

    available_configs = []
    for product in products:
        configs_for_product = create_available_configs_for_product(
            db, product, basic_configs
        )
        available_configs += configs_for_product

    add_all_to_db(db, products + available_configs)

    return products


@fixture(scope="function")
def valid_test_products_with_soldered_ram(
    db: Session,  # noqa
    valid_test_manufacturer: ManufacturerDbModel,
) -> list[ProductDbModel]:
    products = []
    for _id in range(0, 4):
        product = ProductDbModel(
            _id=_id + 10,
            name=f"Test product №{_id}",
            description="test test" * _id,
            price=100_000 - 30_000 * _id,
            count=2 * _id,
            manufacturer=valid_test_manufacturer,
            manufacturer_id=valid_test_manufacturer.id,
            resolution="1366x768",
            resolution_name="HD",
            cpu="i5-8350U",
            gpu="",
            touch_screen=False,
            cpu_speed="test",
            cpu_graphics="test",
            soldered_ram=8,
            can_add_ram=True if _id % 2 == 0 else False,
        )
        products.append(product)
    add_all_to_db(db, products)

    available_configs = []
    for product in products:
        configs = get_product_configs_for_ram(db, product.soldered_ram, product.can_add_ram) 
        configs_for_product = create_available_configs_for_product(
            db, product, configs
        )
        available_configs += configs_for_product

    add_all_to_db(db, products + available_configs)

    return products

