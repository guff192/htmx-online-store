from uuid import uuid4
from fastapi import HTTPException
from loguru import logger
from pytest import fixture, raises
from sqlalchemy.orm import Session

from db_models.cart import CartProductDbModel  # noqa F401
from db_models.product import ProductDbModel
from db_models.user import UserDbModel
from exceptions.cart_exceptions import ErrCantAddProductToCart, ErrCartProductNotFound
from repository.cart_repository import CartRepository, cart_repository_dependency
from repository.product_repository import ProductRepository
from repository.user_repository import UserRepository
from tests.fixtures.db_fixtures import db_session, tables, engine  # noqa F401
from tests.fixtures.db_model_fixtures.cart import (
    invalid_test_cart_product,  # noqa F401
    valid_test_cart_product,  # noqa F401
)
from tests.fixtures.db_model_fixtures.product_configuration import (
    valid_test_configs,  # noqa F401
    valid_test_config_type,  # noqa F401
)
from tests.fixtures.db_model_fixtures.manufacturer import valid_test_manufacturer  # noqa F401
from tests.fixtures.db_model_fixtures.product import valid_test_product  # noqa F401
from tests.fixtures.db_model_fixtures.user import valid_test_user  # noqa F401
from tests.fixtures.logging_fixtures import setup_logger  # noqa F411
from tests.fixtures.repository_fixtures import (
    cart_repo,  # noqa F401
    product_repo,  # noqa F401
    user_repo,  # noqa F401
    configuration_repo,  # noqa F401
)
from tests.helpers.logging_helpers import log_test_info


# Tests
def log_info():
    log_test_info("Testing BannerRepository methods", level=2)


class TestGetUserProducts:
    @fixture(scope="class")
    def log_info(self, db_session: Session):  # noqa F811
        log_test_info("Testing CartRepository.get_user_products() method")
        yield

    def test_with_valid_cart_product(
        self,
        cart_repo: CartRepository,  # noqa F811
        valid_test_cart_product: CartProductDbModel,  # noqa F811
    ):
        logger.info("Testing with valid cart product")

        user_id = str(valid_test_cart_product.user_id)
        found_cart_products = cart_repo.get_user_products(user_id)

        assert len(found_cart_products) == 1
        first_found_cart_product = found_cart_products[0]
        assert first_found_cart_product.id == int(str(valid_test_cart_product.id))
        assert first_found_cart_product.product_id == valid_test_cart_product.product_id

    def test_with_invalid_cart_product(
        self,
        cart_repo: CartRepository,  # noqa F811
        invalid_test_cart_product: CartProductDbModel,  # noqa F811
    ):
        logger.info("Testing with invalid cart product")

        user_id = str(invalid_test_cart_product.user_id)
        found_cart_products = cart_repo.get_user_products(user_id)

        assert len(found_cart_products) == 0


class TestGetProductInCart:
    @fixture(scope="class")
    def log_info(self, db_session: Session):  # noqa F811
        log_test_info("Testing CartRepository.get_product_in_cart() method")
        yield

    def test_with_valid_cart_product(
        self,
        cart_repo: CartRepository,  # noqa F811
        valid_test_cart_product: CartProductDbModel,  # noqa F811
    ):
        logger.info("Testing with valid cart product")

        user_id = str(valid_test_cart_product.user_id)
        product_id = int(str(valid_test_cart_product.product_id))
        configuration_ids = list(
            set(
                int(str(cart_product_config.configuration_id))
                for cart_product_config in valid_test_cart_product.configurations
            )
        )

        found_cart_product = cart_repo.get_product_in_cart(
            user_id, product_id, configuration_ids
        )

        assert found_cart_product.id == int(str(valid_test_cart_product.id))
        assert found_cart_product.product_id == valid_test_cart_product.product_id

    def test_with_invalid_cart_product(
        self,
        cart_repo: CartRepository,  # noqa F811
        invalid_test_cart_product: CartProductDbModel,  # noqa F811
    ):
        logger.info("Testing with invalid cart product")

        user_id = str(invalid_test_cart_product.user_id)
        product_id = int(str(invalid_test_cart_product.product_id))
        configuration_ids = list(
            set(
                int(str(cart_product_config.configuration_id))
                for cart_product_config in invalid_test_cart_product.configurations
            )
        )

        with raises(HTTPException) as raises_context:
            cart_repo.get_product_in_cart(user_id, product_id, configuration_ids)

        assert raises_context.type is ErrCartProductNotFound, (
            f"Expected ErrCartProductNotFound, got {raises_context.type}"
        )

    def test_without_cart_products(
        self,
        cart_repo: CartRepository,  # noqa F811
    ):
        logger.info("Testing without cart products")

        user_id = str(uuid4())
        product_id = 1
        configuration_ids = []

        with raises(HTTPException) as raises_context:
            cart_repo.get_product_in_cart(user_id, product_id, configuration_ids)

        assert raises_context.type is ErrCartProductNotFound, (
            f"Expected ErrCartProductNotFound, got {raises_context.type}"
        )


class TestAddToCart:
    @fixture(scope="class")
    def log_info(self, db_session: Session):  # noqa F811
        log_test_info("Testing CartRepository.add_to_cart() method")
        yield

    def test_with_existing_cart_product(
        self,
        cart_repo: CartRepository,  # noqa F811
        valid_test_cart_product: CartProductDbModel,  # noqa F811
    ):
        logger.info("Testing with existing cart product")

        cart_product_id = int(str(valid_test_cart_product.id))
        user_id = str(valid_test_cart_product.user_id)
        product_id = int(str(valid_test_cart_product.product_id))
        configuration_ids = list(
            set(
                int(str(cart_product_config.configuration_id))
                for cart_product_config in valid_test_cart_product.configurations
            )
        )
        initial_quantity = int(str(valid_test_cart_product.count))

        added_cart_product = cart_repo.add_to_cart(
            user_id, product_id, configuration_ids
        )
        assert added_cart_product.id == cart_product_id
        assert added_cart_product.product_id == product_id
        assert added_cart_product.quantity == initial_quantity + 1

    def test_with_non_existing_cart_product(
        self,
        cart_repo: CartRepository,  # noqa F811
        valid_test_user: UserDbModel,  # noqa F811
        valid_test_product: ProductDbModel,  # noqa F811
    ):
        logger.info("Testing with non existing cart product")

        user_id = str(valid_test_user.id)
        product_id = int(str(valid_test_product._id))
        configuration_ids = list(
            set(
                int(str(available_product_config.configuration_id))
                for available_product_config in valid_test_product.available_configurations
            )
        )

        added_cart_product = cart_repo.add_to_cart(
            user_id, product_id, configuration_ids
        )
        assert added_cart_product.id is not None
        assert added_cart_product.product_id == product_id
        assert added_cart_product.quantity == 1

    def test_with_invalid_cart_product(
        self,
        cart_repo: CartRepository,  # noqa F811
        invalid_test_cart_product: CartProductDbModel,  # noqa F811
    ):
        logger.info("Testing with invalid user id")

        user_id = str(invalid_test_cart_product.user_id)
        product_id = int(str(invalid_test_cart_product.product_id))
        configuration_ids = list(
            set(
                int(str(cart_product_config.configuration_id))
                for cart_product_config in invalid_test_cart_product.configurations
            )
        )

        with raises(HTTPException) as raises_context:
            cart_repo.add_to_cart(user_id, product_id, configuration_ids)

        assert raises_context.type is ErrCantAddProductToCart, (
            f"Expected ErrCantAddProductToCart, got {raises_context.type}"
        )


class TestRemoveFromCart:
    @fixture(scope="class")
    def log_info(self, db_session: Session):  # noqa F811
        log_test_info("Testing CartRepository.remove_from_cart() method")
        yield

    def test_with_existing_cart_product(
        self,
        cart_repo: CartRepository,  # noqa F811
        valid_test_cart_product: CartProductDbModel,  # noqa F811
    ):
        logger.info("Testing with existing cart product")

        cart_product_id = int(str(valid_test_cart_product.id))
        user_id = str(valid_test_cart_product.user_id)
        product_id = int(str(valid_test_cart_product.product_id))
        configuration_ids = list(
            set(
                int(str(cart_product_config.configuration_id))
                for cart_product_config in valid_test_cart_product.configurations
            )
        )
        initial_quantity = int(str(valid_test_cart_product.count))

        removed_cart_product = cart_repo.remove_from_cart(
            user_id, product_id, configuration_ids
        )
        assert removed_cart_product.id == cart_product_id
        assert removed_cart_product.product_id == product_id
        assert removed_cart_product.quantity == initial_quantity - 1

        if initial_quantity == 1:
            try:
                found_cart_product = cart_repo.get_product_in_cart(
                    user_id, product_id, configuration_ids
                )
            except Exception as e:
                assert isinstance(e, ErrCartProductNotFound), (
                    f"Expected ErrCartProductNotFound, got {type(e)}."
                )
                return

            assert found_cart_product is None, (
                "The product should be deleted, but it was found and no exception was raised."
            )

    def test_with_non_existing_cart_product(
        self,
        cart_repo: CartRepository,  # noqa F811
        valid_test_user: UserDbModel,  # noqa F811
        valid_test_product: ProductDbModel,  # noqa F811
    ):
        logger.info("Testing with non existing cart product")

        user_id = str(valid_test_user.id)
        product_id = int(str(valid_test_product._id))
        configuration_ids = list(
            set(
                int(str(available_product_config.configuration_id))
                for available_product_config in valid_test_product.available_configurations
            )
        )

        with raises(HTTPException) as raises_context:
            cart_repo.remove_from_cart(user_id, product_id, configuration_ids)

        assert raises_context.type is ErrCartProductNotFound, (
            f"Expected ErrCartProductNotFound, got {raises_context.type}"
        )


class TestCartRepositoryDependency:
    @fixture(scope="class")
    def log_info(self):
        log_test_info("Testing CartRepository dependency")
        yield

    def test_cart_repository_dependency(self):
        repo = next(cart_repository_dependency())
        assert isinstance(repo, CartRepository)
