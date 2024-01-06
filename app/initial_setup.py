from fastapi import HTTPException
from loguru import logger
import requests
from sqlalchemy.orm import Session

from app.config import Settings
from repository.product_repository import ProductRepository
from schema.product_schema import ProductCreate
from services.product_service import ProductService
from storage.photo_storage import S3ProductPhotoStorage


settings = Settings()


def fetch_products(db: Session):
    # Fetch data from Google Spreadsheet via REST API
    logger.info("Fetching data from Google Spreadsheet...")
    response = requests.get(settings.posting_endpoint)
    data = response.json()

    # Initialize the service and repository
    product_repository = ProductRepository(db)
    product_service = ProductService(product_repository, S3ProductPhotoStorage())

    for product_data in data:
        name = product_data["name"]
        description = product_data["description"]
        price = product_data["basicPrice"]
        if not name or not price or price == '#N/A':
            continue
        # Validate data using the schema
        product_create = ProductCreate(
            name=name,
            description=description,
            price=price
        )

        try:
            # Use the service to create the product
            product_service.create(product_create)
        except HTTPException as e:
            logger.info(f"Error creating product: {e.detail}")

