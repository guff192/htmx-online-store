from pytest import fixture
from sqlalchemy.orm import Session

from db_models.cart import CartProductConfigurationDbModel, CartProductDbModel
from db_models.product import ProductDbModel
from db_models.product_configuration import ProductConfigurationDbModel
from db_models.user import UserDbModel
from tests.fixtures.db_fixtures import db_session  # noqa F401
from tests.fixtures.db_model_fixtures.product_configuration import valid_test_configs  # noqa F401
from tests.fixtures.db_model_fixtures.product import valid_test_product  # noqa F401
from tests.fixtures.db_model_fixtures.user import valid_test_user  # noqa F401
from tests.helpers.db_helpers import add_all_to_db, add_to_db



@fixture(scope="function", params=[1, 2])
def valid_test_cart_product(
    request,
    db_session: Session,  # noqa F811
    valid_test_user: UserDbModel,  # noqa F811
    valid_test_product: ProductDbModel,  # noqa F811
) -> CartProductDbModel:
    cart_product = CartProductDbModel(
        user_id=valid_test_user.id,
        product_id=valid_test_product._id,
        count=request.param
    )
    add_to_db(db_session, cart_product)

    cart_product_configs: list[CartProductConfigurationDbModel] = []
    for available_config in valid_test_product.available_configurations:
        cart_product_config = CartProductConfigurationDbModel(
            cart_product=cart_product,
            configuration=available_config.configuration,
        )
        cart_product_configs.append(cart_product_config)
    add_all_to_db(db_session, cart_product_configs)

    return cart_product


@fixture(scope="function")
def invalid_test_cart_product(
    db_session: Session,  # noqa F811
    valid_test_user: UserDbModel,  # noqa F811
    valid_test_product: ProductDbModel,  # noqa F811
) -> CartProductDbModel:
    cart_product = CartProductDbModel(
        user_id=valid_test_user.id,
        product_id=valid_test_product._id,
        count=-100
    )
    add_to_db(db_session, cart_product)

    cart_product_configs: list[CartProductConfigurationDbModel] = []
    for available_config in valid_test_product.available_configurations:
        cart_product_config = CartProductConfigurationDbModel(
            cart_product_id=cart_product.id,
            cart_product=cart_product,
            configuration_id=available_config.configuration.id,
            configuration=available_config.configuration,
        )
        cart_product_configs.append(cart_product_config)
    add_all_to_db(db_session, cart_product_configs)

    return cart_product
