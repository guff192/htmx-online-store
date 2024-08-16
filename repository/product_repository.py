from typing import Generator
from fastapi import Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from db.session import db_dependency
from dto.product_dto import ProductDTO
from models.product import AvailableProductConfiguration, Product, ProductConfiguration
from models.manufacturer import Manufacturer
from models.user import UserProduct
from repository.configuration_repository import (
    ConfigurationRepository, configuration_repository_dependency
)


class ProductRepository:
    def __init__(
        self,
        db: Session,
        configuration_repository: ConfigurationRepository
    ):
        self.db = db
        self._configuration_repository = configuration_repository


    def get_all(self, offset: int) -> list[ProductDTO]:
        orm_product_dicts = map(
            lambda p: p.__dict__ if p else {},
            self.db.query(Product).slice(offset, offset + 10).all()
        )

        dto_list: list[ProductDTO] = []
        for product_dict in orm_product_dicts:
            product_id = product_dict.get('_id', 0)

            configurations = (self._configuration_repository.
                              get_configurations_for_product(product_id))
            default_configuration_id = product_dict.get(
                'default_configuration_id',
                0
            )
            selected_configuration = list(filter(
                lambda c: c.id == default_configuration_id,
                configurations
            ))[0] if default_configuration_id else None

            manufacturer_id = product_dict.get('manufacturer_id', 0)
            manufacturer_id = manufacturer_id if manufacturer_id else 0

            dto_list.append(
                ProductDTO(
                    id=product_id,
                    name=product_dict.get('name', ''),
                    description=product_dict.get('description', ''),
                    price=product_dict.get('price', 0),
                    count=product_dict.get('count', 0),
                    manufacturer_id=manufacturer_id,
                    configurations=configurations,
                    selected_configuration=selected_configuration,
                )
            )

        return dto_list

    def get_all_with_cart_info(
        self,
        user_id: str,
        offset: int
    ) -> list[ProductDTO]:
        result: list[ProductDTO] = []

        # Create query
        stmt = (
            select(Product._id, Product.name, Product.description,
                   Product.price, Product.manufacturer_id,
                   UserProduct.count, UserProduct.selected_configuration_id).
            join(UserProduct,  # joining for getting count from user_product
                 Product._id == UserProduct.product_id,
                 isouter=True).
            filter(  # filtering products in cart and products without user
                or_(UserProduct.user_id == user_id,
                    UserProduct.user_id == None)).  # noqa: E711
            filter(Product.count > 0).
            order_by(Product.name).
            slice(offset, offset + 10)
        )

        # Execute and add to result
        rows = self.db.execute(stmt).all()
        for row in rows:
            id_, name, description, price, manufacturer_id, user_count, selected_configuration_id = row

            manufacturer_id = manufacturer_id if manufacturer_id else 0
            user_count = user_count if user_count else 0
            selected_configuration_id = selected_configuration_id if selected_configuration_id else 0

            configs = (self._configuration_repository.
                              get_configurations_for_product(id_))

            if not configs:
                continue

            selected_config = tuple(filter(
                lambda c: c.id == selected_configuration_id or selected_configuration_id == 0,
                configs
            ))[0]

            product = ProductDTO(
                id=id_, name=name, description=description,
                price=price, count=user_count,
                manufacturer_id=manufacturer_id,
                configurations=configs,
                selected_configuration=selected_config
            )
            result.append(product)

        return result

    def get_newcomers(self, offset: int) -> list[Product]:
        product_list = (
            self.db.query(Product).
            filter(Product.newcomer == True).  # noqa: E712
            slice(offset, offset + 10).all()
        )

        return product_list

    def get_by_id(self, product_id) -> Product | None:
        return self.db.query(Product).get(product_id)

    def get_by_name(self, name: str) -> Product | None:
        return self.db.query(Product).filter(Product.name == name).first()

    def search(self, query: str, offset: int) -> list[Product]:
        return self.db.query(Product).\
            filter(Product.name.like(f'%{query.replace(" ", "%")}%')).slice(offset, offset + 10).all()

    def create(self,
               name: str,
               description: str,
               price: int,
               count: int = 0,
               manufacturer: Manufacturer | None = None,
               configurations: list[ProductConfiguration] = []
    ) -> Product:
        product = Product(
            name=name,
            description=description,
            price=price,
            count=count,
            manufacturer=manufacturer,
        )
        self.db.add(product)
        self.db.flush([product])

        configs: list[AvailableProductConfiguration] = []
        for config in configurations:
            available_configuration = AvailableProductConfiguration(
                product_id=product._id,
                configuration=config
            )
            self.db.add(available_configuration)
            configs.append(available_configuration)
        self.db.commit()
        self.db.flush(configs)

        product = self.get_by_id(product._id)
        return product

    def update(self,
               id: int,
               name: str,
               description: str,
               price: int,
               count: int,
               manufacturer: Manufacturer,
               configurations: list[ProductConfiguration]) -> int:

        transaction = self.db.begin(nested=True)
        updated_product_query = self.db.query(Product).filter(
            Product._id == id
        )
        found_product = updated_product_query.first()
        if not found_product:
            transaction.rollback()
            return 0

        updated_products_count = updated_product_query.update({
            'name': name,
            'description': description,
            'price': price,
            'count': count,
            'manufacturer_id': manufacturer.id,
        })

        found_config_ids = map(lambda available_config: available_config.id,
            found_product.configurations)
        update_config_ids = map(lambda available_config: available_config.id,
            configurations)
        if set(found_config_ids) != set(update_config_ids):
            self.db.query(AvailableProductConfiguration).\
                filter(AvailableProductConfiguration.product_id == id).\
                delete()
            for config in configurations:
                available_configuration = AvailableProductConfiguration(
                    product=updated_product_query.first(), configuration=config
                )
                self.db.add(available_configuration)


        transaction.commit()

        return updated_products_count


def product_repository_dependency(
    db: Session = Depends(db_dependency),
    configuration_repo: ConfigurationRepository = Depends(
        configuration_repository_dependency
    )
) -> Generator[ProductRepository, None, None]:
    repo = ProductRepository(db, configuration_repo)
    yield repo


def test_product_repository():
    USER_ID = 'a7e02df8-e3d8-4aa5-bc52-ce70fb214647'
    session = next(db_dependency())
    repo = ProductRepository(session, ConfigurationRepository(session))

    for product in repo.get_all_with_cart_info(USER_ID, 10):
        print(product.__dict__)

