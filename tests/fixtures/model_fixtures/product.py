from pytest import fixture

from models.manufacturer import Manufacturer
from models.product import AvailableProductConfiguration, Product
from models.product_configuration import ProductConfiguration
from tests.fixtures.model_fixtures.product_configuration import (
    test_configuration_type_model,  # noqa F401
    test_product_configurations_model,  # noqa F401
)
from tests.fixtures.model_fixtures.manufacturer import test_manufacturer_model  # noqa F401


@fixture(scope="function")
def test_available_product_configurations_model(
    test_product_configurations_model: list[ProductConfiguration],  # noqa F811
) -> list[AvailableProductConfiguration]:
    return [
        AvailableProductConfiguration(
            id=1,
            configuration=config,
        )
        for config in test_product_configurations_model
    ]


@fixture(scope="function")
def test_product_model_with_basic_data(
    test_manufacturer_model: Manufacturer,  # noqa F811
    test_available_product_configurations_model: list[AvailableProductConfiguration],  # noqa F811
) -> Product:
    return Product(
        id=1,
        name="Test Product",
        description="Test Product Description",
        specifications=None,
        count=10,
        newcomer=False,
        manufacturer=test_manufacturer_model,
        available_configurations=test_available_product_configurations_model,
    )
