from pytest import fixture

from models.cart import CartProduct
from models.product import Product
from models.product_configuration import ProductConfiguration
from tests.fixtures.model_fixtures.product_configuration import test_product_configurations_model  # noqa F401
from tests.fixtures.model_fixtures.product import test_product_model_with_basic_data  # noqa F401
from tests.fixtures.model_fixtures.user import test_user_model_with_basic_data  # noqa F401


@fixture(scope="function")
def test_cart_product_model_with_basic_data(
    test_product_model_with_basic_data: Product,  # noqa F811
    test_product_configurations_model: list[ProductConfiguration],  # noqa F811
) -> CartProduct:
    return CartProduct(
        id=1,
        product_id=test_product_model_with_basic_data.id,
        quantity=1,
        selected_configurations=test_product_configurations_model,
    )
