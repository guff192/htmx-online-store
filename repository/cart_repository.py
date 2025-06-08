from collections.abc import Generator
from typing import Any, TypeVar

from fastapi import Depends
from loguru import logger
from pydantic import ValidationError
from sqlalchemy import (
    Delete,
    Insert,
    Integer,
    Row,
    ScalarSelect,
    Select,
    Subquery,
    Update,
    cast,
    delete,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from db.session import db_dependency, get_db
from exceptions.cart_exceptions import ErrCantAddProductToCart, ErrCartProductNotFound
from exceptions.product_exceptions import ErrProductNotFound
from db_models.product import ProductDbModel
from db_models.cart import CartProductConfigurationDbModel, CartProductDbModel
from models.cart import CartProduct
from repository.configuration_repository import ConfigurationRepository
from repository.product_repository import (
    ProductRepository,
    get_product_repository,
    product_repository_dependency,
)
from repository.user_repository import (
    UserRepository,
    get_user_repository,
    user_repository_dependency,
)


CART_QUERY_TYPE = TypeVar("CART_QUERY_TYPE", Select, Update, Delete)


class CartRepository:
    def __init__(
        self, db: Session, product_repo: ProductRepository, user_repo: UserRepository
    ) -> None:
        self._db = db
        self._product_repo = product_repo
        self._user_repo = user_repo

    def _get_cart_product_select_query(
        self,
    ) -> Select[tuple[CartProductDbModel]]:
        return select(CartProductDbModel)

    def _get_cart_product_update_query(
        self,
    ) -> Update:
        return update(CartProductDbModel)

    def _get_cart_product_insert_query(
        self,
    ) -> Insert:
        return insert(CartProductDbModel)

    def _get_cart_product_delete_query(
        self,
    ) -> Delete:
        return delete(CartProductDbModel)

    def _get_configuration_insert_query(
        self,
    ) -> Insert:
        return insert(CartProductConfigurationDbModel)

    def _get_configurations_delete_query(self, cart_product_id: int) -> Delete:
        return delete(CartProductConfigurationDbModel).where(
            CartProductConfigurationDbModel.cart_product_id == cart_product_id
        )

    def _add_cart_product_id_to_query(
        self, query: CART_QUERY_TYPE, cart_product_id: int
    ) -> CART_QUERY_TYPE:
        return query.filter(CartProductDbModel.id == cart_product_id)

    def _add_user_id_to_query(
        self, query: CART_QUERY_TYPE, user_id: str
    ) -> CART_QUERY_TYPE:
        return query.filter(CartProductDbModel.user_id == user_id)

    def _add_product_id_to_query(
        self, query: CART_QUERY_TYPE, product_id: int
    ) -> CART_QUERY_TYPE:
        return query.filter(CartProductDbModel.product_id == product_id)

    def _add_configuration_ids_to_query(
        self, query: Select[tuple[CartProductDbModel]], configuration_ids: list[int]
    ) -> Select[tuple[CartProductDbModel]]:
        sorted_configuration_ids = sorted(configuration_ids)
        input_array_literal = cast(sorted_configuration_ids, postgresql.ARRAY(Integer))

        existing_configs_subquery = (
            select(
                postgresql.array_agg(
                    CartProductConfigurationDbModel.configuration_id,
                    order_by=CartProductConfigurationDbModel.configuration_id,
                )
            )
            .where(
                CartProductConfigurationDbModel.cart_product_id == CartProductDbModel.id
            )
            .scalar_subquery()
        )

        return query.filter(existing_configs_subquery == input_array_literal)

    def get_user_products(self, user_id: str) -> list[CartProduct]:
        query = self._get_cart_product_select_query()
        query = self._add_user_id_to_query(query, user_id)

        domain_model_cart_products: list[CartProduct] = []
        result = self._db.execute(query)
        for orm_cart_product in result.scalars().all():
            try:
                cart_product = CartProduct.model_validate(orm_cart_product)
                domain_model_cart_products.append(cart_product)
            except ValidationError:
                continue

        return domain_model_cart_products

    def get_product_in_cart(
        self, user_id: str, product_id: int, configuration_ids: list[int]
    ) -> CartProduct:
        query = self._get_cart_product_select_query()
        query = self._add_user_id_to_query(query, user_id)
        query = self._add_product_id_to_query(query, product_id)

        result = self._db.execute(query)

        try:
            orm_cart_product = result.scalar_one()
            cart_product = CartProduct.model_validate(orm_cart_product)
        except (NoResultFound, ValidationError):
            raise ErrCartProductNotFound

        return cart_product

    def add_to_cart(
        self, user_id: str, product_id: int, configuration_ids: list[int]
    ) -> CartProduct:
        select_query = select(CartProductDbModel)
        select_query = self._add_user_id_to_query(select_query, user_id)
        select_query = self._add_product_id_to_query(select_query, product_id)
        select_query = self._add_configuration_ids_to_query(
            select_query, configuration_ids
        )

        search_result = self._db.execute(select_query)
        orm_cart_product = search_result.scalar_one_or_none()
        if not orm_cart_product:
            cart_product_insert_query = self._get_cart_product_insert_query()
            cart_product_insert_query = cart_product_insert_query.values(
                user_id=user_id, product_id=product_id
            )
            result = self._db.execute(cart_product_insert_query)
            inserted_pk = result.inserted_primary_key[0]  # type: ignore

            configs_insert_query = self._get_configuration_insert_query()
            configs_insert_values = []
            for configuration_id in configuration_ids:
                configs_insert_values.append(
                    {
                        "cart_product_id": inserted_pk,
                        "configuration_id": configuration_id,
                    }
                )
            configs_insert_query = configs_insert_query.values(configs_insert_values)
            self._db.execute(configs_insert_query)
        else:
            found_cart_product_id = int(str(orm_cart_product.id))
            update_query = self._get_cart_product_update_query()
            update_query = self._add_cart_product_id_to_query(
                update_query, found_cart_product_id
            )
            update_query = update_query.values(
                {CartProductDbModel.count: CartProductDbModel.count + 1}
            )
            self._db.execute(update_query)

        search_result = self._db.execute(select_query)
        try:
            updated_product_orm: CartProductDbModel = search_result.scalar_one()
            updated_product = CartProduct.model_validate(updated_product_orm)
        except (NoResultFound, ValidationError):
            self._db.rollback()
            raise ErrCantAddProductToCart

        self._db.commit()

        return updated_product

    def remove_from_cart(
        self,
        user_id: str,
        product_id: int,
        configuration_ids: list[int],
    ) -> CartProduct:
        select_query = self._get_cart_product_select_query()
        select_query = self._add_user_id_to_query(select_query, user_id)
        select_query = self._add_product_id_to_query(select_query, product_id)
        select_query = self._add_configuration_ids_to_query(
            select_query, configuration_ids
        )

        result = self._db.execute(select_query)
        orm_found_cart_product = result.scalar_one_or_none()
        try:
            found_cart_product = CartProduct.model_validate(orm_found_cart_product)
            assert found_cart_product.id is not None
        except (ValidationError, AssertionError):
            raise ErrCartProductNotFound

        # Check if removing last product
        if found_cart_product.quantity == 1:
            configs_delete_query = self._get_configurations_delete_query(
                found_cart_product.id
            )
            self._db.execute(configs_delete_query)

            delete_query = self._get_cart_product_delete_query()
            delete_query = self._add_cart_product_id_to_query(
                delete_query, found_cart_product.id
            )
            self._db.execute(delete_query)
        else:
            update_query = self._get_cart_product_update_query()
            update_query = self._add_cart_product_id_to_query(
                update_query, found_cart_product.id
            )
            update_query = update_query.values(
                {CartProductDbModel.count: CartProductDbModel.count - 1}
            )
            self._db.execute(update_query)

        self._db.commit()

        found_cart_product.quantity = found_cart_product.quantity - 1
        return found_cart_product


def cart_repository_dependency(
    db: Session = Depends(db_dependency),
    product_repo: ProductRepository = Depends(product_repository_dependency),
    user_repo: UserRepository = Depends(user_repository_dependency),
) -> Generator[CartRepository, None, None]:
    repo = CartRepository(db, product_repo, user_repo)
    yield repo


def get_cart_repository(
    db: Session = get_db(),
    product_repo: ProductRepository = get_product_repository(),
    user_repo: UserRepository = get_user_repository(),
):
    return CartRepository(db, product_repo, user_repo)
