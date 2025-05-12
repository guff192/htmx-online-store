from boto3.exceptions import Boto3Error
from botocore.exceptions import EndpointConnectionError
from fastapi import Depends
from loguru import logger
from pydantic_core import Url

from dto.product_dto import ProductDTO
from exceptions.product_exceptions import (
    ErrInvalidProduct,
    ErrProductNotFound,
)
from exceptions.product_prices_exceptions import ErrPriceNotFound
from db_models.product import ProductDbModel, ProductConfigurationDbModel
from db_models.manufacturer import ManufacturerDbModel
from repository.configuration_repository import ConfigurationRepository, configuration_repository_dependency
from repository.manufacturer_repository import ManufacturerRepository, manufacturer_repository_dependency
from repository.product_repository import (
    ProductRepository,
    product_repository_dependency,
)
from schema.manufacturer_schema import Manufacturer as ManufacturerSchema
from schema.product_schema import (
    Product as ProductSchema,
    ProductCreate,
    ProductList,
    ProductPhotoPath,
    ProductPhotoSize,
    ProductPrices,
    ProductUpdateResponse,
    ProductConfiguration as ProductConfigurationSchema,
)
from schema.cart_schema import ProductInCart
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

    def _orm_configuration_to_config_schema(self, orm_config: ProductConfigurationDbModel) -> ProductConfigurationSchema:
        config_dict = orm_config.__dict__
        id = config_dict.get('id', 0)
        ram_amount = config_dict.get('ram_amount', 0)
        ssd_amount = config_dict.get('ssd_amount', 0)
        additional_price = config_dict.get('additional_price', 0)
        is_default = config_dict.get('is_default', False)
        additional_ram = config_dict.get('additional_ram', False)
        soldered_ram = config_dict.get('soldered_ram', 0)

        return ProductConfigurationSchema(
            id=id,
            ram_amount=ram_amount,
            ssd_amount=ssd_amount,
            additional_price=additional_price,
            is_default=is_default,
            additional_ram=additional_ram,
            soldered_ram=soldered_ram
        )

    def _orm_product_to_product_schema(self, orm_product: ProductDbModel) -> ProductSchema:
        product_dict = orm_product.__dict__
        manufacturer_dict = orm_product.manufacturer.__dict__
        manufacturer_schema = ManufacturerSchema(
            name=manufacturer_dict.get('name', ''),
            logo_url=manufacturer_dict.get('logo_url', '')
        )
        soldered_ram = product_dict.get('soldered_ram', 0)
        can_add_ram = product_dict.get('can_add_ram', False)
        resolution = product_dict.get('resolution', '')
        cpu = product_dict.get('cpu', '')
        gpu = product_dict.get('gpu', '')
        touchscreen = product_dict.get('touch_screen', False)

        return ProductSchema(
            id=product_dict.get('_id', 0),
            name=product_dict.get('name', ''),
            description=product_dict.get('description', ''),
            price=product_dict.get('price', 0),
            manufacturer=manufacturer_schema,
            soldered_ram=soldered_ram,
            can_add_ram=can_add_ram,
            resolution=resolution,
            cpu=cpu,
            gpu=gpu,
            touch_screen=touchscreen
        )

    def _product_dto_to_productincart_schema(self, product_dto: ProductDTO) -> ProductInCart:
            # searching manufacturer
            manufacturer_id = product_dto.manufacturer_id
            if not manufacturer_id:
                manufacturer_id = 0

            manufacturer = self._manufacturer_repo.get_by_id(manufacturer_id)
            if not manufacturer:
                raise NotImplementedError

            manufacturer_dict = manufacturer.__dict__
            manufacturer_name = manufacturer_dict.get('name', '')
            manufacturer_logo_url = manufacturer_dict.get('logo_url', '')
            manufacturer_schema = ManufacturerSchema(
                name=manufacturer_name, logo_url=manufacturer_logo_url
            )

            configurations = [ProductConfigurationSchema(
                id=configuration.id,
                ram_amount=configuration.ram_amount,
                ssd_amount=configuration.ssd_amount,
                additional_price=configuration.additional_price,
                is_default=configuration.is_default,
                additional_ram=configuration.additional_ram,
                soldered_ram=configuration.soldered_ram
            ) for configuration in product_dto.configurations]
            selected_configuration = ProductConfigurationSchema(
                id=product_dto.selected_configuration.id,
                ram_amount=product_dto.selected_configuration.ram_amount,
                ssd_amount=product_dto.selected_configuration.ssd_amount,
                additional_price=product_dto.selected_configuration.additional_price,
                is_default=product_dto.selected_configuration.is_default,
                additional_ram=product_dto.selected_configuration.additional_ram,
                soldered_ram=product_dto.selected_configuration.soldered_ram
            ) if product_dto.selected_configuration else None

            product_in_cart = ProductInCart(
                id=product_dto.id, name=product_dto.name,
                description=product_dto.description,
                price=product_dto.price, count=product_dto.count,
                manufacturer=manufacturer_schema,
                configurations=configurations,
                selected_configuration=selected_configuration
            )
            return product_in_cart

    def get_config_by_id(self, config_id: int) -> ProductConfigurationDbModel:
        return self.config_repo.get_by_id(config_id)
    
    def get_available_configurations(
        self,
        additional_ram: bool = False,
        soldered_ram: int = 0
    ) -> list[ProductConfigurationSchema]:
        orm_configs = self.config_repo.get_available_configurations(additional_ram, soldered_ram)

        schema_configs: list[ProductConfigurationSchema] = []
        for config in orm_configs:
            schema_config = self._orm_configuration_to_config_schema(config)
            schema_configs.append(schema_config)

        return schema_configs

    def get_all_basic_configs(
        self
    ):
        orm_configs = self.config_repo.get_default_configurations()

        schema_configs: list[ProductConfigurationSchema] = []
        for config in orm_configs:
            schema_config = self._orm_configuration_to_config_schema(config)

            schema_configs.append(schema_config)

        return schema_configs

    def get_configurations_for_product(
        self,
        product_id: int
    ) -> list[ProductConfigurationSchema]:
        return [
            ProductConfigurationSchema(
                id=config.id,
                ram_amount=config.ram_amount,
                ssd_amount=config.ssd_amount,
                additional_price=config.additional_price,
                is_default=config.is_default,
                additional_ram=config.additional_ram,
                soldered_ram=config.soldered_ram
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
        query: str,
        offset: int,
        user: LoggedUser | None = None,
        price_from: int = 0, price_to: int = 150000,
        ram: list[int] = [], ssd: list[int] = [], cpu: list[str] = [],
        resolution: list[str] = [], touchscreen: list[bool] = [],
        graphics: list[bool] = [],
    ) -> ProductList:
        if offset < 0:
            raise ErrProductNotFound()

        # getting dto list from repository
        if user:
            dto_list = self.repo.get_all_with_cart_info(
                query, str(user.id), offset,
                price_from=price_from, price_to=price_to,
                ram=ram, ssd=ssd, cpu=cpu, resolution=resolution,
                touchscreen=touchscreen, graphics=graphics
            )
        else:
            dto_list = self.repo.get_all(
                query=query, offset=offset,
                price_from=price_from, price_to=price_to,
                ram=ram, ssd=ssd, cpu=cpu, resolution=resolution,
                touchscreen=touchscreen, graphics=graphics
            )

        # checking dto list
        if not dto_list:
            return ProductList(products=[], offset=-5)
        if len(dto_list) == 1 and dto_list[0].id == -5:
            return ProductList(products=[], offset=offset+10)

        # creating products list
        products: list[ProductInCart] = []
        for product_dto in dto_list:
            product = self._product_dto_to_productincart_schema(product_dto)
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
            # getting manufacturer
            if not hasattr(orm_product, 'manufacturer'):
                continue

            manufacturer = orm_product.manufacturer
            manufacturer_dict = manufacturer.__dict__
            manufacturer_name = manufacturer_dict.get('name', '')
            manufacturer_logo_url = manufacturer_dict.get('logo_url', '')
            manufacturer_schema = ManufacturerSchema(
                name=manufacturer_name, logo_url=manufacturer_logo_url
            )

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
                manufacturer=manufacturer_schema
            )
            schema_products.append(product)

        return ProductList(products=schema_products, offset=offset + 10)

    def get_by_id(self, product_id: int) -> ProductSchema:
        orm_product = self.repo.get_by_id(product_id)
        if not orm_product:
            raise ErrProductNotFound(product_id)
        product_schema = self._orm_product_to_product_schema(orm_product)

        available_configurations = self.get_configurations_for_product(
            product_id
        )
        product_schema.configurations = available_configurations

        return product_schema

    def get_by_name(self, name: str) -> ProductDbModel:
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
        product_update: ProductCreate
    ) -> ProductUpdateResponse:
        # getting configurations
        if product_update.can_add_ram is None or product_update.soldered_ram is None:
            logger.debug(f'Invalid product - no information about soldered RAM: {product_update}')
            raise ErrInvalidProduct()

        update_model_configurations: list[ProductConfigurationDbModel] = self.config_repo.get_available_configurations(
            additional_ram=product_update.can_add_ram,
            soldered_ram=product_update.soldered_ram
        )
        if not update_model_configurations:
            logger.debug(f'Invalid product - no configurations found: {product_update}')
            raise ErrInvalidProduct()
        product_update.configurations = self.get_available_configurations(
            product_update.can_add_ram,
            product_update.soldered_ram
        )

        if not product_update.is_valid():
            logger.debug(f'Invalid product - not valid: {product_update}')
            raise ErrInvalidProduct()

        # searching manufacturer
        manufacturer: ManufacturerDbModel = self._manufacturer_repo.get_by_name(
            product_update.manufacturer_name
        )
        if not manufacturer:
            logger.debug(f'Invalid product - no such manufacturer: {product_update.manufacturer_name = }')
            raise ErrInvalidProduct()

        # getting additional specs
        name = product_update.name
        description = product_update.description
        count = product_update.count
        price = product_update.price
        soldered_ram = product_update.soldered_ram
        can_add_ram = product_update.can_add_ram
        resolution = product_update.resolution if product_update.resolution else ''
        resolution_name = product_update.resolution_name
        cpu = product_update.cpu if product_update.cpu else ''
        gpu = product_update.gpu if product_update.gpu else ''
        touch_screen = product_update.touch_screen if product_update.touch_screen is not None else False
        cpu_speed = product_update.cpu_speed if product_update.cpu_speed else ''
        cpu_graphics = product_update.cpu_graphics if product_update.cpu_graphics else ''

        # searching product
        found_product: ProductDbModel | None = self.repo.get_by_name(product_update.name)
        if not found_product:
            # creating new product
            logger.debug(f'Creating new product: {product_update}')
            self.repo.create(
                name, description, price, count=count,
                manufacturer=manufacturer, configurations=update_model_configurations,
                soldered_ram=soldered_ram, can_add_ram=can_add_ram,
                resolution=resolution, resolution_name=resolution_name if resolution_name else '',
                cpu=cpu, gpu=gpu, touch_screen=touch_screen,
                cpu_speed=cpu_speed, cpu_graphics=cpu_graphics,
            )
            return ProductUpdateResponse(count=1)

        # updating product
        logger.debug(f'Updating product (in service): {found_product.__dict__}')
        updated_products_count = self.repo.update(
            id=found_product.__dict__['_id'],
            name=name, description=description, price=price, count=count,
            manufacturer=manufacturer,
            configurations=update_model_configurations,
            soldered_ram=soldered_ram,
            can_add_ram=can_add_ram,
            resolution=resolution, resolution_name=resolution_name if resolution_name else '',
            cpu=cpu,
            gpu=gpu,
            touch_screen=touch_screen,
            cpu_speed=cpu_speed, cpu_graphics=cpu_graphics,
        )
        return ProductUpdateResponse(count=updated_products_count)

    def search(self, name: str, offset: int = 0) -> ProductList:
        orm_products = self.repo.search(name, offset)
        schema_products: list[ProductSchema] = []
        for orm_product in orm_products:
            product_schema = self._orm_product_to_product_schema(orm_product)
            schema_products.append(product_schema)

        product_list = ProductList(products=schema_products, offset=offset)
        return product_list


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

