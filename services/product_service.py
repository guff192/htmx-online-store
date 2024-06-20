from fastapi import Depends
from loguru import logger
from pydantic_core import Url

from exceptions.product_exceptions import (
    ErrInvalidProduct,
    ErrProductAlreadyExists,
    ErrProductNotFound,
)
from exceptions.product_prices_exceptions import ErrPriceNotFound
from models.product import Product, ProductConfiguration
from models.manufacturer import Manufacturer
from models.user import UserProduct
from repository.configuration_repository import ConfigurationRepository, configuration_repository_dependency
from repository.manufacturer_repository import ManufacturerRepository, manufacturer_repository_dependency
from repository.product_repository import (
    ProductRepository,
    product_repository_dependency,
)
from schema.product_schema import (
    Product as ProductSchema,
    ProductCreate,
    ProductInCart,
    ProductList,
    ProductPhotoPath,
    ProductPhotoSize,
    ProductPrices,
    ProductUpdate,
    ProductUpdateResponse,
    ProductConfiguration as ProductConfigurationSchema,
)
from schema.user_schema import LoggedUser
from storage.photo_storage import (
    ProductPhotoStorage,
    product_photo_storage_dependency
)


class ProductService:
    def __init__(
        self,
        product_repo: ProductRepository,
        photo_storage: ProductPhotoStorage,
        manufacturer_repo: ManufacturerRepository,
        configuration_repo: ConfigurationRepository
    ):
        self.repo = product_repo
        self._manufacturer_repo = manufacturer_repo
        self.config_repo = configuration_repo
        self.photo_storage = photo_storage

    def get_config_by_id(self, config_id: int) -> ProductConfiguration:
        return self.config_repo.get_by_id(config_id)
    
    def get_configs_by_names(self, names: list[str]) -> list[ProductConfiguration]:
        return self.config_repo.get_configurations_by_names(names)

    def get_all_basic_configs(
        self
    ):
        orm_configs = self.config_repo.get_default_configurations()

        schema_configs: list[ProductConfigurationSchema] = []
        for config in orm_configs:
            config_dict = config.__dict__
            id = config_dict.get('id')
            name = config_dict.get('name')
            additional_price = config_dict.get('additional_price')
            if not id or not name or additional_price is None:
                continue

            schema_configs.append(
                ProductConfigurationSchema(
                    id=id,
                    name=name,
                    additional_price=additional_price
                )
            )

        return schema_configs

    def get_configurations_for_product(
        self,
        product_id: int
    ) -> list[ProductConfigurationSchema]:
        return [
            ProductConfigurationSchema(
                id=config.id,
                name=config.name,
                additional_price=config.additional_price
            )
            for config in self.config_repo.get_configurations_for_product(product_id)
        ]


    def get_product_prices(
        self,
        product_id: int,
        configuration_id: int
    ) -> ProductPrices:
        # searching product
        product = self.repo.get_by_id(product_id)
        if not product:
            raise ErrProductNotFound()

        # searching available configurations
        configurations = self.get_configurations_for_product(product_id)

        # searching selected configuration
        try:
            selected_configuration = list(filter(
                lambda c: c.id == configuration_id, configurations
            ))[0] if configuration_id else configurations[0]
        except IndexError:
            raise ErrPriceNotFound()

        return ProductPrices(
                product_id=product.__dict__.get('_id', 0),
                basic_price=product.__dict__.get('price', 0),
                configurations=configurations,
                selected_configuration=selected_configuration
            )

    def get_all(
        self,
        offset: int,
        user: LoggedUser | None = None
    ) -> ProductList:
        if offset < 0:
            raise ErrProductNotFound()

        if user:
            dto_list = self.repo.get_all_with_cart_info(str(user.id), offset)
        else:
            dto_list = self.repo.get_all(offset=offset)

        if not dto_list:
            return ProductList(products=[], offset=-5)

        # Creating products list
        products: list[ProductInCart] = []
        for product_dto in dto_list:
            # searching manufacturer
            manufacturer_id = product_dto.manufacturer_id
            if not manufacturer_id:
                manufacturer_id = 0

            manufacturer = self._manufacturer_repo.get_by_id(manufacturer_id)
            if not manufacturer:
                manufacturer_name = ''
            else:
                manufacturer_name = manufacturer.__dict__.get('name', '')

            product = ProductInCart(
                id=product_dto.id, name=product_dto.name,
                description=product_dto.description,
                price=product_dto.price, count=product_dto.count,
                manufacturer_name=manufacturer_name,
            )
            products.append(product)

        product_list = ProductList(
            offset=offset + 10,
            products=products,
        )

        return product_list

    def get_newcomers(self, offset: int) -> ProductList:
        orm_products = self.repo.get_newcomers(offset=offset)

        schema_products: list[ProductSchema] = []
        for orm_product in orm_products:
            # getting manufacturer name
            manufacturer_name = ''
            if hasattr(orm_product, 'manufacturer'):
                manufacturer = orm_product.manufacturer
                if manufacturer and manufacturer.__dict__:
                    manufacturer_name = manufacturer.__dict__.get('name', '')

            orm_product_dict = orm_product.__dict__
            product_id = orm_product_dict.get('_id', 0)
            product_name = orm_product_dict.get('name', '')
            product_photos = self.get_all_photos_by_name(product_name)

            product = ProductSchema(
                id=product_id,
                photos=product_photos,
                name=product_name,
                description=orm_product_dict.get('description', ''),
                price=orm_product_dict.get('price', 0),
                manufacturer_name=manufacturer_name,
            )
            schema_products.append(product)

        return ProductList(products=schema_products, offset=offset + 10)

    def get_by_id(self, product_id: int) -> ProductSchema:
        orm_product = self.repo.get_by_id(product_id)
        if not orm_product:
            raise ErrProductNotFound()
        orm_product_dict = orm_product.__dict__

        product_name = orm_product_dict.get('name', '')
        try:
            product_photos = self.get_all_photos_by_name(product_name)
        except:
            product_photos = []

        manufacturer_name = ''
        if hasattr(orm_product, 'manufacturer') and orm_product.manufacturer:
            manufacturer: Manufacturer = orm_product.manufacturer
            if manufacturer:
                manufacturer_name = manufacturer.__dict__.get('name', '')
        
        available_configurations = self.get_configurations_for_product(
            product_id
        )

        product_schema = ProductSchema(
            id=orm_product_dict.get('_id', 0),
            photos=product_photos,
            name=product_name,
            description=orm_product_dict.get('description', ''),
            price=orm_product_dict.get('price', 0),
            manufacturer_name=manufacturer_name,
            configurations=available_configurations,
            selected_configuration=None
        )
        return product_schema

    def get_by_name(self, name: str) -> Product:
        return self.repo.get_by_name(name)

    def get_url_by_photo_path(
        self,
        photo_path: ProductPhotoPath,
    ) -> Url:
        return self.photo_storage.get_url(photo_path)

    def get_main_photo(
        self,
        product_name: str,
        size: ProductPhotoSize = ProductPhotoSize.small
    ) -> ProductPhotoPath | None:
        result = self.photo_storage.get_main_photo_by_name(product_name, size)

        return result

    def get_all_photos_by_name(
        self,
        name: str,
        size: ProductPhotoSize = ProductPhotoSize.thumbs
    ) -> list[ProductPhotoPath]:
        return self.photo_storage.get_all_by_name(name, size)

    def update_or_create_by_name(
        self,
        product_update: ProductUpdate
    ) -> ProductUpdateResponse:
        if not product_update.is_valid():
            logger.debug(f'Invalid product: {product_update}')
            raise ErrInvalidProduct()

        # searching manufacturer
        manufacturer: Manufacturer = self._manufacturer_repo.get_by_name(
            product_update.manufacturer_name
        )
        if not manufacturer:
            logger.debug(f'Invalid product: {product_update}')
            raise ErrInvalidProduct()

        # getting configurations
        update_configurations: list[ProductConfiguration] = self.get_configs_by_names(
            list(map(lambda x: x.name, product_update.configurations))
        )

        # searching product
        found_product: Product | None = self.repo.get_by_name(product_update.name)
        if not found_product:
            # creating new product
            logger.debug(f'Creating new product: {product_update}')
            self.repo.create(
                product_update.name,
                product_update.description,
                product_update.price,
                count=product_update.count,
                manufacturer=manufacturer,
                configurations=update_configurations
            )
            return ProductUpdateResponse(count=1)

        # updating product
        logger.debug(f'Updating product: {found_product.__dict__}')
        updated_products_count = self.repo.update(
            id=found_product.__dict__['_id'],
            name=product_update.__dict__.get("name", ""),
            description=product_update.__dict__.get("description", ""),
            price=product_update.__dict__.get("price", ""),
            count=product_update.__dict__.get("count", ""),
            manufacturer=manufacturer,
            configurations=update_configurations
        )
        return ProductUpdateResponse(count=updated_products_count)

    def search(self, name: str) -> list[Product]:
        return self.repo.search(name)

    def create(self, product_create_schema: ProductCreate) -> ProductSchema:
        if not product_create_schema.is_valid():
            logger.error(f'invalid product: {product_create_schema}')
            raise ErrInvalidProduct()

        found_product = self.repo.get_by_name(product_create_schema.name)
        if found_product:
            product_id = found_product.__dict__.get('_id', '')

            created_product = ProductUpdate(
                name=product_create_schema.name,
                description=product_create_schema.description,
                price=product_create_schema.price,
                count=product_create_schema.count,
                manufacturer_name=product_create_schema.manufacturer_name,
                configurations=product_create_schema.configurations,
            )
            self.update_or_create_by_name(created_product)

            product_schema = ProductSchema(
                id=product_id,
                name=created_product.name,
                description=created_product.description,
                price=created_product.price,
                manufacturer_name=product_create_schema.manufacturer_name,
                configurations=product_create_schema.configurations,
            )

        else:
            created_product = self.repo.create(
                name=product_create_schema.name,
                description=product_create_schema.description,
                price=product_create_schema.price,
                count=product_create_schema.count,
                manufacturer=self._manufacturer_repo.get_by_name(
                    product_create_schema.manufacturer_name
                )
            )
            product_id: int = created_product.__dict__.get('_id', -1)

            product_schema = ProductSchema(
                id=product_id,
                name=created_product.__dict__.get('name', ''),
                description=created_product.__dict__.get('description', ''),
                price=created_product.__dict__.get('price', ''),
                manufacturer_name=product_create_schema.manufacturer_name,
            )

        return product_schema


def product_service_dependency(
    product_repo: ProductRepository = Depends(product_repository_dependency),
    photo_storage: ProductPhotoStorage = Depends(
        product_photo_storage_dependency
    ),
    manufacturer_repo: ManufacturerRepository = Depends(
        manufacturer_repository_dependency
    ),
    configuration_repo: ConfigurationRepository = Depends(
        configuration_repository_dependency
    )
):
    service = ProductService(product_repo, photo_storage, manufacturer_repo,
                             configuration_repo)
    yield service

