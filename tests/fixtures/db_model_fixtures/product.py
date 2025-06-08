from pytest import fixture
from sqlalchemy.orm import Session

from db_models.manufacturer import ManufacturerDbModel
from db_models.product import ProductDbModel
from db_models.product_configuration import ProductConfigurationDbModel
from tests.fixtures.db_fixtures import db_session, engine, tables  # noqa F401
from tests.fixtures.db_model_fixtures.manufacturer import valid_test_manufacturer  # noqa F401
from tests.fixtures.db_model_fixtures.product_configuration import valid_test_configs  # noqa F401
from tests.helpers.configurations_helpers import create_available_configs_for_product
from tests.helpers.db_helpers import add_all_to_db, add_to_db


@fixture(scope="function")
def valid_test_product(
    db_session: Session,  # noqa F811
    valid_test_manufacturer: ManufacturerDbModel,  # noqa F811
    valid_test_configs: list[ProductConfigurationDbModel],  # noqa F811
) -> ProductDbModel:
    product = ProductDbModel(
        _id=1,
        name="test",
        description="test",
        price=100000 - 30000,
        count=20,
        newcomer=True,
        manufacturer=valid_test_manufacturer,
        manufacturer_id=valid_test_manufacturer.id,
    )
    add_to_db(db_session, product)

    create_available_configs_for_product(db_session, product, valid_test_configs)

    return product


@fixture(scope="function")
def valid_test_products(
    db_session: Session,  # noqa
    valid_test_manufacturer: ManufacturerDbModel,  # noqa F811
    valid_test_configs: list[ProductConfigurationDbModel],  # noqa F811
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

    add_all_to_db(db_session, products)
    
    for product in products:
        create_available_configs_for_product(
            db_session, product, valid_test_configs
        )

    return products


@fixture(scope="function")
def invalid_test_product(
    db_session: Session,  # noqa F811
    valid_test_manufacturer: ManufacturerDbModel,  # noqa F811
    valid_test_configs: list[ProductConfigurationDbModel],  # noqa F811
):  # noqa
    product = ProductDbModel(
        _id=1,
        name="test",
        description="test",
        price=1000,
        count=-1,
        manufacturer=valid_test_manufacturer,
        manufacturer_id=valid_test_manufacturer.id,
        newcomer=True,
    )
    add_to_db(db_session, product)

    create_available_configs_for_product(db_session, product, valid_test_configs)

    return product
