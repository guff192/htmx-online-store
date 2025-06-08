from pydantic_core import Url
from pytest import fixture

from models.product_configuration import ConfigurationType, ProductConfiguration


@fixture(scope="function")
def test_configuration_type_model() -> ConfigurationType:
    return ConfigurationType(
        id=1,
        name="Test Configuration Type",
        image_url=Url("https://example.com/image.png"),
    )


@fixture(scope="function")
def test_product_configuration_model(
    test_configuration_type_model: ConfigurationType,
) -> ProductConfiguration:
    return ProductConfiguration(
        id=1,
        short_name="Test Configuration",
        additional_price=10000,
        type=test_configuration_type_model,
        value="Test Value",
    )


@fixture(scope="function")
def test_product_configurations_model(
    test_configuration_type_model: ConfigurationType,
) -> list[ProductConfiguration]:
    return [
        ProductConfiguration(
            id=i,
            short_name=f"Test Configuration {i}",
            additional_price=10000 * i,
            type=test_configuration_type_model,
            value=f"Test Value {i}",
        )
        for i in range(1, 4)
    ]
