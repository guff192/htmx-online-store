"""Create configurations

Revision ID: 34f06bf855e8
Revises: eeb0956f71d5
Create Date: 2024-10-30 01:16:40.332791

"""
from typing import Sequence, Union

from alembic import op

from app.config import Settings


# revision identifiers, used by Alembic.
revision: str = '34f06bf855e8'
down_revision: Union[str, None] = 'eeb0956f71d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

settings = Settings()


def upgrade() -> None:
    stmt = """
        INSERT INTO product_configurations (ram_amount, ssd_amount, additional_price, is_default, additional_ram, soldered_ram)
        VALUES 
        (0, 0, 0, 1, 0, 0),
        (4, 128, 2000, 1, 0, 0),
        (8, 256, 4000, 1, 0, 0),
        (16, 512, 8000, 1, 0, 0),
        (32, 1024, 16000, 1, 0, 0),

        (4, 128, 1000, 0, 1, 4),
        (8, 256, 3000, 0, 1, 4),
        (12, 256, 4000, 0, 1, 4),
        (12, 512, 6000, 0, 1, 4),
        (20, 512, 8000, 0, 1, 4),
        (20, 1024, 12000, 0, 1, 4),

        (8, 256, 2000, 0, 1, 8),
        (12, 256, 3000, 0, 1, 8),
        (12, 512, 5000, 0, 1, 8),
        (16, 512, 6000, 0, 1, 8),
        (24, 512, 8000, 0, 1, 8),
        (24, 1024, 12000, 0, 1, 8),

        (16, 512, 4000, 0, 1, 16),
        (20, 512, 5000, 0, 1, 16),
        (24, 512, 6000, 0, 1, 16),
        (24, 1024, 10000, 0, 1, 16),
        (32, 1024, 12000, 0, 1, 16),
        
        (4, 128, 1000, 0, 0, 4),
        (4, 256, 2000, 0, 0, 4),
        (4, 512, 4000, 0, 0, 4),
        (4, 1024, 8000, 0, 0, 4),

        (8, 128, 1000, 0, 0, 8),
        (8, 256, 2000, 0, 0, 8),
        (8, 512, 4000, 0, 0, 8),
        (8, 1024, 8000, 0, 0, 8),

        (16, 128, 1000, 0, 0, 16),
        (16, 256, 2000, 0, 0, 16),
        (16, 512, 4000, 0, 0, 16),
        (16, 1024, 8000, 0, 0, 16),

        (32, 128, 1000, 0, 0, 32),
        (32, 256, 2000, 0, 0, 32),
        (32, 512, 4000, 0, 0, 32),
        (32, 1024, 8000, 0, 0, 32);
    """
    if "sqlite" not in settings.db_url:
        stmt.replace(";", "\nON CONFLICT (name) DO NOTHING;")

    op.execute(stmt)


def downgrade() -> None:
    op.execute("DELETE FROM product_configurations;")

