import subprocess
from fastapi import HTTPException
from loguru import logger
import requests
from requests.exceptions import JSONDecodeError
from sqlalchemy.orm import Session
from repository.configuration_repository import ConfigurationRepository

from .config import Settings
from db.session import db_dependency
from repository.manufacturer_repository import ManufacturerRepository
from repository.product_repository import ProductRepository
from schema.product_schema import ProductCreate
from services.product_service import ProductService
from storage.photo_storage import S3ProductPhotoStorage


settings = Settings()


def fetch_products(db: Session):
    # Fetch data from Google Spreadsheet via REST API
    logger.info("Fetching data from Google Spreadsheet...")
    response = requests.get(settings.posting_endpoint)
    try:
        data = response.json()
    except JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response from Google Spreadsheets: {e}")
        logger.error(f"Unparsed response: {e.response}")
        return

    # Initialize the service and repository
    product_repository = ProductRepository(db, ConfigurationRepository(db))
    manufacturer_repository = ManufacturerRepository(db)
    configuration_repository = ConfigurationRepository(db)
    product_service = ProductService(
        product_repository, S3ProductPhotoStorage(), manufacturer_repository,
        configuration_repository
    )

    basic_configs = product_service.get_all_basic_configs()
    logger.debug(f'{basic_configs = }')

    for product_data in data:
        name = product_data.get("name", "")
        description = product_data.get("description", "")
        price = product_data.get("price", 0)
        count = product_data.get("count", 0)
        manufacturer_name = product_data.get("manufacturer_name", "")
        use_basic_configs = product_data.get("basic_configs", False)
        soldered_ram = product_data.get("soldered_ram", 0)
        can_add_ram = product_data.get("can_add_ram", False)
        resolution = product_data.get("resolution", "")
        resolution_name = product_data.get("resolution_name", "")
        cpu = product_data.get("cpu", "")
        gpu = product_data.get("gpu", "")
        touch_screen = product_data.get("touch_screen", False)
        cpu_speed = product_data.get("cpu_speed", "")
        cpu_graphics = product_data.get("cpu_graphics", "")
        if not name or not price or price == '#N/A' or \
                soldered_ram is None or can_add_ram is None or \
                not cpu or gpu is None or touch_screen is None:
            logger.info(f"Skipping product: {product_data}")
            continue

        if use_basic_configs:
            configurations = basic_configs
        else:
            configurations = product_service.get_available_configurations(
                additional_ram=can_add_ram,
                soldered_ram=soldered_ram
            )

        # Validate data using the schema
        product_create = ProductCreate(
            name=name,
            description=description,
            price=price,
            count=count if count != '#N/A' else 0,
            manufacturer_name=manufacturer_name,
            configurations=configurations,
            soldered_ram=soldered_ram,
            can_add_ram=can_add_ram,
            resolution=resolution,
            resolution_name=resolution_name,
            cpu=cpu,
            gpu=gpu,
            touch_screen=touch_screen,
            cpu_speed=cpu_speed,
            cpu_graphics=cpu_graphics
        )

        try:
            # Use the service to create the product
            count = product_service.update_or_create_by_name(product_create)
            logger.info(f"Created product: {product_create}")
        except HTTPException as e:
            logger.info(f"Error creating product: {e.detail}")


def reload_tailwindcss():
    """Reload the TailwindCSS CSS file."""
    try:
        subprocess.run([
            'npx',
            '@tailwindcss/cli',
            '-i',
            str(settings.static_dir / 'src' / 'tw.css'),
            '-o',
            str(settings.static_dir / 'css' / 'main.css'),
        ])
    except Exception as e:
        print(f'Error running tailwindcss: {e}')


def run_migrations():
    """Run Alembic migrations to ensure database is up to date."""
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logger.info("Database migrations applied successfully.")
    except Exception as e:
        logger.error(f"Error applying migrations: {e}")


if __name__ == "__main__":
    with next(db_dependency()) as db:
        fetch_products(db)

