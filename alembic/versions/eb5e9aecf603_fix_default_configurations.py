"""Fix default configurations

Revision ID: eb5e9aecf603
Revises: 05fce9675e76
Create Date: 2024-11-01 02:47:45.872115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.config import Settings


# revision identifiers, used by Alembic.
revision: str = 'eb5e9aecf603'
down_revision: Union[str, None] = '05fce9675e76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

settings = Settings()


def upgrade() -> None:
    stmt = """
        UPDATE product_configurations
        SET additional_ram = {true}
        WHERE is_default = {true}
    """
    stmt = stmt.format(
        true="true" if "postgres" in settings.db_url else "1",
        false="false" if "postgres" in settings.db_url else "0"
    )

    op.execute(stmt)


def downgrade() -> None:
    stmt = """
        UPDATE product_configurations
        SET additional_ram = {false}
        WHERE is_default = {true}
    """
    stmt = stmt.format(
        true="true" if "postgres" in settings.db_url else "1",
        false="false" if "postgres" in settings.db_url else "0"
    )
    op.execute(stmt)

