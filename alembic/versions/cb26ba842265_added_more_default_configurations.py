"""Added more default configurations

Revision ID: cb26ba842265
Revises: 62982f1b3964
Create Date: 2024-11-13 17:04:42.758683

"""
from typing import Sequence, Union

from alembic import op

from app.config import Settings


# revision identifiers, used by Alembic.
revision: str = 'cb26ba842265'
down_revision: Union[str, None] = '62982f1b3964'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

settings = Settings()


def upgrade() -> None:
    stmt = """
        INSERT INTO product_configurations (ram_amount, ssd_amount, additional_price, is_default, additional_ram, soldered_ram)
        VALUES 
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
        (32, 512, 12000, {true}, {true}, 0);
    """
    stmt = stmt.format(
        true="true" if "postgres" in settings.db_url else "1",
        false="false" if "postgres" in settings.db_url else "0"
    )
    op.execute(stmt)


def downgrade() -> None:
    stmt = """
        DELETE FROM product_configurations
        WHERE is_default = {true} AND
        (ram_amount = 4 AND ssd_amount = 256) OR
        (ram_amount = 4 AND ssd_amount = 512) OR
        (ram_amount = 4 AND ssd_amount = 1024) OR
        (ram_amount = 8 AND ssd_amount = 128) OR
        (ram_amount = 8 AND ssd_amount = 512) OR
        (ram_amount = 8 AND ssd_amount = 1024) OR
        (ram_amount = 16 AND ssd_amount = 128) OR
        (ram_amount = 16 AND ssd_amount = 256) OR
        (ram_amount = 16 AND ssd_amount = 1024) OR
        (ram_amount = 32 AND ssd_amount = 128) OR
        (ram_amount = 32 AND ssd_amount = 256) OR
        (ram_amount = 32 AND ssd_amount = 512);
    """
    op.execute(stmt)

