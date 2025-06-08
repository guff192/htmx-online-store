from pydantic_core import Url
from pytest import fixture

from models.manufacturer import Manufacturer


@fixture(scope="function")
def test_manufacturer_model() -> Manufacturer:
    return Manufacturer(
        id=1,
        name="Test Manufacturer",
        logo_url=Url("https://example.com/logo.png"),
    )
