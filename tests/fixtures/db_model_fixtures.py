from pytest import fixture
from sqlalchemy.orm import Session

from db_models.banner import BannerDbModel
from db_models.manufacturer import ManufacturerDbModel
from db_models.product import ProductDbModel
from db_models.product_configuration import (
    ConfigurationTypeDbModel,
    ProductConfigurationDbModel,
)

from tests.helpers.db_helpers import add_to_db, add_all_to_db
from tests.helpers.configurations_helpers import create_available_configs_for_product


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
def invalid_test_config(db: Session, valid_test_config_type: ConfigurationTypeDbModel):  # noqa
    config = ProductConfigurationDbModel(
        id=0,
        additional_price=-1000,
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
    valid_test_configs: list[ProductConfigurationDbModel],
) -> ProductDbModel:
    product = ProductDbModel(
        _id=request.param,
        name="test",
        description="test" * request.param,
        price=100000 - 30000 * request.param,
        count=100 - 30 * request.param,
        newcomer=True if request.param % 2 == 0 else False,
        manufacturer=valid_test_manufacturer,
        manufacturer_id=valid_test_manufacturer.id,
    )
    add_to_db(db, product)

    create_available_configs_for_product(db, product, valid_test_configs)

    return product


@fixture(scope="function")
def valid_test_products(
    db: Session,  # noqa
    valid_test_manufacturer: ManufacturerDbModel,
    valid_test_configs: list[ProductConfigurationDbModel],
) -> list[ProductDbModel]:
    products: list[ProductDbModel] = []
    for i in range(1, 4):
        product = ProductDbModel(
            _id=i,
            name=f"test {i}",
            description="test",
            price=100000 - 30000 * i,
            count=100 - 30 * i,
            newcomer=True if i % 2 == 0 else False,
            manufacturer=valid_test_manufacturer,
            manufacturer_id=valid_test_manufacturer.id,
        )
        products.append(product)
        add_to_db(db, product)
        create_available_configs_for_product(db, products[0], valid_test_configs)

    return products


@fixture(scope="function", params=[x + 1 for x in range(3)])
def invalid_test_product(
    request,
    db: Session,
    valid_test_manufacturer: ManufacturerDbModel,
    valid_test_configs: list[ProductConfigurationDbModel],
):  # noqa
    product = ProductDbModel(
        _id=request.param,
        name=f"test {request.param}",
        description="test",
        price=request.param * 1000 * -(1**request.param),
        count=-1,
        manufacturer=valid_test_manufacturer,
        manufacturer_id=valid_test_manufacturer.id,
        newcomer=True,
    )
    add_to_db(db, product)

    create_available_configs_for_product(db, product, valid_test_configs)

    return product


@fixture(scope="function")
def valid_test_banner(db: Session):
    banner = BannerDbModel(
        _id=1,
        name="test",
        description="test banner",
        img_url="http://example.com",
    )
    add_to_db(db, banner)

    return banner


@fixture(scope="function")
def invalid_test_banner(db: Session):
    banner = BannerDbModel(
        _id=1,
        name="test",
        description="test banner",
        img_url="not a url",
    )
    add_to_db(db, banner)

    return banner


@fixture(scope="function")
def valid_test_banners(db: Session):
    banners: list[BannerDbModel] = []
    for i in range(1, 4):
        banners.append(BannerDbModel(
            _id=i,
            name=f"test{i}",
            description=f"test banner {i}",
            img_url=f"http://example.com/{i}",
        ))

    add_all_to_db(db, banners)
    
    return banners
