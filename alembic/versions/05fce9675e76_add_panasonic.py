"""Add panasonic

Revision ID: 05fce9675e76
Revises: 34f06bf855e8
Create Date: 2024-10-30 03:43:56.961116

"""
from typing import Sequence, Union

from alembic import op

from app.config import Settings


# revision identifiers, used by Alembic.
revision: str = '05fce9675e76'
down_revision: Union[str, None] = '34f06bf855e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

settings = Settings()


def upgrade() -> None:
    stmt = """
        INSERT INTO manufacturers (name, logo_url)
        VALUES 
        ('Panasonic', 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Panasonic_logo_%28Blue%29.svg/2880px-Panasonic_logo_%28Blue%29.svg.png');
    """
    if "sqlite" not in settings.db_url:
        stmt.replace(";", "\nON CONFLICT (name) DO NOTHING;")

    op.execute(stmt)    


def downgrade() -> None:
    op.execute("""
        DELETE FROM manufacturers 
        WHERE name = 'Panasonic';
    """)

