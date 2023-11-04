import requests
from sqlalchemy.orm import Session

from app.config import Settings
from repository.product_repository import ProductRepository
from schema.product_schema import ProductCreate
from services.product_service import ProductService


settings = Settings()


def fetch_and_load_products(db: Session):
    # Fetch data from Google Spreadsheet via REST API
    response = requests.get(settings.posting_endpoint)
    data = response.json()

    # Initialize the service and repository
    product_repository = ProductRepository(db)
    product_service = ProductService(product_repository)

    for product_data in data:
        # Validate data using the schema
        product_create = ProductCreate(
            name=product_data["name"],
            description=product_data["description"],
            price=product_data["basicPrice"]
        )
        
        # Use the service to create the product
        product_service.create(product_create)

