from collections.abc import Generator

from fastapi import Depends
from loguru import logger
from sqlalchemy.orm import Query, Session

from db.session import db_dependency
from exceptions.product_exceptions import ErrProductNotFound
from db_models.product import ProductDbModel
from db_models.user import UserProductDbModel
from repository.configuration_repository import ConfigurationRepository
from repository.product_repository import (
    ProductRepository,
    product_repository_dependency,
)
from repository.user_repository import (
    UserRepository,
    user_repository_dependency
)


class CartRepository:
    def __init__(
            self, db: Session,
            product_repo: ProductRepository,
            user_repo: UserRepository
    ) -> None:
        self._db = db
        self._product_repo = product_repo
        self._user_repo = user_repo

    def _get_user_product_query(
            self,
            user_id: str,
            product_id: int,
            configuration_id: int = 0
    ) -> Query[UserProductDbModel]:
        query_without_configuration = (
            self._db
            .query(UserProductDbModel)
            .filter(UserProductDbModel.user_id == user_id)
            .filter(UserProductDbModel.product_id == product_id)
            .filter(UserProductDbModel.selected_configuration_id == configuration_id)
        )

        if not configuration_id:
            return query_without_configuration
        return (
            query_without_configuration
            .filter(UserProductDbModel.selected_configuration_id == configuration_id)
        )

    def get_user_products(self, user_id: str) -> list[UserProductDbModel]:
        user_products = (
            self._db.query(UserProductDbModel).
            join(ProductDbModel).
            filter(UserProductDbModel.user_id == user_id).all()
        )

        return user_products

    def get_product_in_cart(self, user_id: str, product_id: int) -> UserProductDbModel | None:
        return (
            self
            ._get_user_product_query(user_id, product_id)
            .first()
        )

    def add_to_cart(
        self, user_id: str, product_id: int, configuration_id: int
    ) -> UserProductDbModel | None:
        found_userproduct_query = self._get_user_product_query(user_id,
                                                     product_id,
                                                     configuration_id)

        # Check if product is not already in cart
        if not found_userproduct_query.first():
            user_product = UserProductDbModel(
                user_id=user_id, product_id=product_id,
                selected_configuration_id=configuration_id, count=1
            )
            self._db.add(user_product)
        else:
            # Increment product count
            found_userproduct_query.update({UserProductDbModel.count: UserProductDbModel.count + 1})

        self._db.commit()
        updated_product: UserProductDbModel | None = (
            self
            ._get_user_product_query(user_id, product_id, configuration_id)
            .first()
        )

        return updated_product

    def remove_from_cart(
            self,
            user_id: str,
            configuration_id: int,
            product_id: int
    ) -> UserProductDbModel:
        found_userproduct_query: Query[UserProductDbModel] = (
            self._get_user_product_query(user_id, product_id, configuration_id)
        )
        if not found_userproduct_query.first():
            raise ErrProductNotFound()

        found_userproduct = found_userproduct_query.first()
        if not found_userproduct:
            raise ErrProductNotFound()

        product = found_userproduct.product
        selected_configuration = found_userproduct.selected_configuration

        # Check if removing last product
        if found_userproduct.__dict__.get('count', 0) == 1:
            found_userproduct_query.delete()
        else:
            found_userproduct_query.update({UserProductDbModel.count: UserProductDbModel.count - 1})

        self._db.flush((found_userproduct_query, ))
        self._db.commit()

        updated_product: UserProductDbModel | None = (
            found_userproduct_query.first()
        )
        if not updated_product:
            updated_product = UserProductDbModel(
                user_id=user_id, product_id=product_id,
                selected_configuration_id=configuration_id, count=0,
                product=product, selected_configuration=selected_configuration
            )

        return updated_product


def cart_repository_dependency(
    db: Session = Depends(db_dependency),
    product_repo: ProductRepository = Depends(product_repository_dependency),
    user_repo: UserRepository = Depends(user_repository_dependency),
) -> Generator[CartRepository, None, None]:
    repo = CartRepository(db, product_repo, user_repo)
    try:
        yield repo
    finally:
        db.close()


def test_cart_repository():
    USER_ID = '5a354f3f-6818-4695-a8e8-98a2a645cd27'
    PRODUCT_ID = 13
    CONFIGURATION_ID = 1
    session = next(db_dependency())
    repo = CartRepository(
        session,
        ProductRepository(session, ConfigurationRepository(session)),
        UserRepository(session)
    )
    user_product = repo.remove_from_cart(USER_ID, PRODUCT_ID, CONFIGURATION_ID)
    logger.debug(user_product)

