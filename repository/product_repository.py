from typing import Generator
from fastapi import Depends
from loguru import logger
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


    def get_all(
        self, offset: int, ram: list[int] = [], ssd: list[int] = [],
        cpu: list[str] = [], resolution: list[str] = [],
        touchscreen: list[bool] = [], graphics: list[bool] = []
    ) -> list[ProductDTO]:
        logger.debug(f'{ram = }\n{ssd = }\n{cpu = }\n{resolution = }\n{touchscreen = }\n{graphics = }\n')
        orm_product_dicts = map(
            lambda p: p.__dict__ if p else {},
            self.db.query(Product).slice(offset, offset + 10).all()
        )

        dto_list: list[ProductDTO] = []
        for product_dict in orm_product_dicts:
            logger.debug(f'{product_dict = }\n')
            product_id = product_dict.get('_id', 0)

            configurations = (self._configuration_repository.
                              get_configurations_for_product(product_id))

            # filtering by ram
            ram_filtered_configurations = list(filter(
                lambda c: c.ram_amount in ram, configurations,
            ))
            if len(ram) > 0 and len(ram_filtered_configurations) == 0:
                logger.debug('skipping because of ram filtering\n')
                continue

            # filtering by ssd
            ssd_filtered_configurations = list(filter(
                lambda c: c.ssd_amount in ssd, configurations
            ))
            if len(ssd) > 0 and len(ssd_filtered_configurations) == 0:
                logger.debug('skipping because of ssd filtering\n\n')
                continue

            # filtering by cpu
            product_cpu = product_dict.get('cpu', '')
            if len(cpu) > 0 and not any(c.lower() in product_cpu.lower() for c in cpu):
                logger.debug('skipping because of cpu filtering\n\n')
                continue
            
            # filtering by resolution
            product_resolution = product_dict.get('resolution', '')
            if len(resolution) > 0 and not product_resolution in resolution:
                logger.debug('skipping because of resolution filtering\n\n')
                continue

            # filtering by touchscreen
            product_touch_screen = product_dict.get('touch_screen', False)
            if len(touchscreen) > 0 and product_touch_screen not in touchscreen:
                logger.debug('skipping because of touchscreen filtering\n\n')
                continue

            # filtering by graphics
            product_gpu = product_dict.get('gpu', '')
            if len(graphics) == 1:
                if True in graphics and not product_gpu:
                    logger.debug('skipping because of graphics filtering\n\n')
                    continue
                if False in graphics and product_gpu:
                    logger.debug('skipping because of graphics filtering\n\n')
                    continue

            product_soldered_ram = product_dict.get('soldered_ram', 0)
            product_can_add_ram = product_dict.get('can_add_ram', True)
            
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
                    soldered_ram=product_soldered_ram,
                    can_add_ram=product_can_add_ram,
                    resolution=product_resolution,
                    cpu=product_cpu,
                    gpu=product_gpu,
                    touch_screen=product_touch_screen
                )
            )

        return dto_list

    def get_all_with_cart_info(
        self,
        user_id: str,
        offset: int,
        ram: list[int] = [], ssd: list[int] = [], cpu: list[str] = [], 
        resolution: list[str] = [], touchscreen: list[bool] = [],
        graphics: list[bool] = [],
    ) -> list[ProductDTO]:
        result: list[ProductDTO] = []

        # Create query
        stmt = (
            select(Product._id, Product.name, Product.description,
                   Product.price, Product.manufacturer_id,
                   Product.soldered_ram, Product.can_add_ram,
                   Product.resolution, Product.cpu, Product.gpu,
                   Product.touch_screen,
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
            id_, product_name, product_description, product_price, \
            product_manufacturer_id, product_soldered_ram, product_can_add_ram, \
            product_resolution, product_cpu, product_gpu, product_touch_screen, \
            user_count, selected_configuration_id = row

            product_manufacturer_id = product_manufacturer_id if product_manufacturer_id else 0
            user_count = user_count if user_count else 0
            selected_configuration_id = selected_configuration_id if selected_configuration_id else 0

            configs = (self._configuration_repository.
                              get_configurations_for_product(id_))
            if not configs:
                continue

            # filtering by ram
            ram_filtered_configurations = list(filter(
                lambda c: c.ram_amount in ram, configs,
            ))
            if len(ram) > 0 and len(ram_filtered_configurations) == 0:
                logger.debug('skipping because of ram filtering\n')
                continue

            # filtering by ssd
            ssd_filtered_configurations = list(filter(
                lambda c: c.ssd_amount in ssd, configs
            ))
            if len(ssd) > 0 and len(ssd_filtered_configurations) == 0:
                logger.debug('skipping because of ssd filtering\n\n')
                continue

            # filtering by cpu
            if len(cpu) > 0 and not any(c.lower() in product_cpu.lower() for c in cpu):
                logger.debug('skipping because of cpu filtering\n\n')
                continue
            
            # filtering by resolution
            if len(resolution) > 0 and not product_resolution in resolution:
                logger.debug('skipping because of resolution filtering\n\n')
                continue

            # filtering by touchscreen
            if len(touchscreen) > 0 and product_touch_screen not in touchscreen:
                logger.debug('skipping because of touchscreen filtering\n\n')
                continue

            # filtering by graphics
            if len(graphics) == 1:
                if True in graphics and not product_gpu:
                    logger.debug('skipping because of graphics filtering\n\n')
                    continue
                if False in graphics and product_gpu:
                    logger.debug('skipping because of graphics filtering\n\n')
                    continue

            selected_config = tuple(filter(
                lambda c: c.id == selected_configuration_id or selected_configuration_id == 0,
                configs
            ))[0]

            product = ProductDTO(
                id=id_, name=product_name, description=product_description,
                price=product_price, count=user_count,
                manufacturer_id=product_manufacturer_id, soldered_ram=product_soldered_ram,
                can_add_ram=product_can_add_ram, resolution=product_resolution, cpu=product_cpu,
                gpu=product_gpu, touch_screen=product_touch_screen,
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
               configurations: list[ProductConfiguration] = [],
               soldered_ram: int = 0,
               can_add_ram: bool = True,
               resolution: str = '',
               cpu: str = '',
               gpu: str = '',
               touch_screen: bool = False
    ) -> Product:
        product = Product(
            name=name,
            description=description,
            price=price,
            count=count,
            manufacturer=manufacturer,
            soldered_ram=soldered_ram,
            can_add_ram=can_add_ram,
            resolution=resolution,
            cpu=cpu,
            gpu=gpu,
            touch_screen=touch_screen
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
               configurations: list[ProductConfiguration],
               soldered_ram: int = 0,
               can_add_ram: bool = True,
               resolution: str = '',
               cpu: str = '',
               gpu: str = '',
               touch_screen: bool = False) -> int:

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
            'soldered_ram': soldered_ram,
            'can_add_ram': can_add_ram,
            'resolution': resolution,
            'cpu': cpu,
            'gpu': gpu,
            'touch_screen': touch_screen
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

