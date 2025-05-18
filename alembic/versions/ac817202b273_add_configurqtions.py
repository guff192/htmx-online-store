"""Add configurqtions

Revision ID: ac817202b273
Revises: 1927acae029d
Create Date: 2024-12-16 22:38:17.782579

"""
from typing import Sequence, Union

from alembic import op

from app.config import Settings


# revision identifiers, used by Alembic.
revision: str = 'ac817202b273'
down_revision: Union[str, None] = '1927acae029d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

settings = Settings()


def upgrade() -> None:
    configuration_types_stmt = """
    INSERT INTO configuration_types (id, name, img_url)
    VALUES
    (1, 'RAM', NULL),
    (2, 'SSD', NULL);
    """

    product_configurations_stmt = """
    INSERT INTO product_configurations (additional_price, short_name, configuration_type_id, value)
    VALUES
    (1000, '4Гб Оперативной Памяти', 1, '4GB'),
    (2000, '8Гб Оперативной Памяти', 1, '8GB'),
    (4000, '16Гб Оперативной Памяти', 1, '16GB'),
    (8000, '32Гб Оперативной Памяти', 1, '32GB'),

    (1000, '128Гб SSD', 2, '128GB'),
    (2000, '256Гб SSD', 2, '256GB'),
    (4000, '512Гб SSD', 2, '512GB'),
    (8000, '1Тб SSD', 2, '1TB');
    """

    for stmt in (configuration_types_stmt, product_configurations_stmt):
        op.execute(stmt)


def downgrade() -> None:
    stmt = """
        DELETE FROM available_product_configurations;
    """
    op.execute(stmt)

    stmt = """
        DELETE FROM order_product_configurations;
        DELETE FROM order_products;
    """
    op.execute(stmt)

    stmt = """
        DELETE FROM cart_product_configurations;
        DELETE FROM cart_products;
    """
    op.execute(stmt)

    stmt = """
        DELETE FROM configuration_types;
        DELETE FROM product_configurations;
    """
    op.execute(stmt)

