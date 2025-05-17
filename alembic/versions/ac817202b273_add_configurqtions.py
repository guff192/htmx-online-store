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
    stmt = """
        INSERT INTO product_configurations (ram_amount, ssd_amount, additional_price, is_default, additional_ram, soldered_ram)
        VALUES 
        (0, 0, 0, {true}, {true}, 0),
        (4, 128, 2000, {true}, {true}, 0),
        (8, 256, 4000, {true}, {true}, 0),
        (16, 512, 8000, {true}, {true}, 0),
        (32, 1024, 16000, {true}, {true}, 0),

        (4, 0, 1000, {true}, {true}, 0),
        (8, 0, 2000, {true}, {true}, 0),
        (16, 0, 4000, {true}, {true}, 0),
        (32, 0, 8000, {true}, {true}, 0),

        (0, 128, 1000, {true}, {true}, 0),
        (0, 256, 2000, {true}, {true}, 0),
        (0, 512, 4000, {true}, {true}, 0),
        (0, 1024, 8000, {true}, {true}, 0),

        (4, 256, 3000, {true}, {true}, 0),
        (4, 512, 5000, {true}, {true}, 0),
        (4, 1024, 9000, {true}, {true}, 0),

        (8, 128, 3000, {true}, {true}, 0),
        (8, 512, 6000, {true}, {true}, 0),
        (8, 1024, 10000, {true}, {true}, 0),

        (16, 128, 5000, {true}, {true}, 0),
        (16, 256, 6000, {true}, {true}, 0),
        (16, 1024, 12000, {true}, {true}, 0),

        (32, 128, 9000, {true}, {true}, 0),
        (32, 256, 10000, {true}, {true}, 0),
        (32, 512, 12000, {true}, {true}, 0),

        (4, 128, 1000, {false}, {true}, 4),
        (8, 256, 3000, {false}, {true}, 4),
        (12, 256, 4000, {false}, {true}, 4),
        (12, 512, 6000, {false}, {true}, 4),
        (20, 512, 8000, {false}, {true}, 4),
        (20, 1024, 12000, {false}, {true}, 4),

        (8, 256, 2000, {false}, {true}, 8),
        (12, 256, 3000, {false}, {true}, 8),
        (12, 512, 5000, {false}, {true}, 8),
        (16, 512, 6000, {false}, {true}, 8),
        (24, 512, 8000, {false}, {true}, 8),
        (24, 1024, 12000, {false}, {true}, 8),

        (16, 512, 4000, {false}, {true}, 16),
        (20, 512, 5000, {false}, {true}, 16),
        (24, 512, 6000, {false}, {true}, 16),
        (24, 1024, 10000, {false}, {true}, 16),
        (32, 1024, 12000, {false}, {true}, 16),
        
        (4, 128, 1000, {false}, {false}, 4),
        (4, 256, 2000, {false}, {false}, 4),
        (4, 512, 4000, {false}, {false}, 4),
        (4, 1024, 8000, {false}, {false}, 4),

        (8, 128, 1000, {false}, {false}, 8),
        (8, 256, 2000, {false}, {false}, 8),
        (8, 512, 4000, {false}, {false}, 8),
        (8, 1024, 8000, {false}, {false}, 8),

        (16, 128, 1000, {false}, {false}, 16),
        (16, 256, 2000, {false}, {false}, 16),
        (16, 512, 4000, {false}, {false}, 16),
        (16, 1024, 8000, {false}, {false}, 16),

        (32, 128, 1000, {false}, {false}, 32),
        (32, 256, 2000, {false}, {false}, 32),
        (32, 512, 4000, {false}, {false}, 32),
        (32, 1024, 8000, {false}, {false}, 32);
    """
    stmt = stmt.format(
        true="true" if "postgres" in settings.db_url else "1",
        false="false" if "postgres" in settings.db_url else "0"
    )
    if "sqlite" not in settings.db_url:
        stmt.replace(";", "\nON CONFLICT (name) DO NOTHING;")

    op.execute(stmt)


def downgrade() -> None:
    stmt = """
        DELETE FROM available_product_configurations
    """
    op.execute(stmt)

    stmt = """
        DELETE FROM order_products
    """
    op.execute(stmt)

    stmt = """
        DELETE FROM user_products
    """
    op.execute(stmt)

    stmt = """
        DELETE FROM product_configurations WHERE
        soldered_ram IN (0, 4, 8, 16, 32)
    """
    op.execute(stmt)

