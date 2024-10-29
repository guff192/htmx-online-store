"""Add configurations

Revision ID: cd3b51b4c2b9
Revises: c77e2efc9311
Create Date: 2024-10-29 20:15:50.103892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.config import Settings


# revision identifiers, used by Alembic.
revision: str = 'cd3b51b4c2b9'
down_revision: Union[str, None] = 'c77e2efc9311'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

settings = Settings()


def upgrade() -> None:
    stmt = """
        INSERT INTO product_configurations (name, additional_price, is_default)
        VALUES 
        ('No RAM/No SSD', 0, 1),
        ('4GB RAM/128GB SSD', 2000, 1),
        ('8GB RAM/256GB SSD', 4000, 1),
        ('16GB RAM/512GB SSD', 8000, 1),
        ('32GB RAM/1TB SSD', 16000, 1);
    """
    if "sqlite" not in settings.db_url:
        stmt.replace(";", "\nON CONFLICT (name) DO NOTHING;")

    op.execute(stmt)



def downgrade() -> None:
    op.execute("""
        DELETE FROM product_configurations 
        WHERE name IN ('No RAM/No SSD', '4GB RAM/128GB SSD', '8GB RAM/256GB SSD', '16GB RAM/512GB SSD', '32GB RAM/1TB SSD');
    """)

