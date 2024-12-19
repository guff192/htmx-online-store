"""Add manufacturers

Revision ID: 1927acae029d
Revises: 
Create Date: 2024-12-16 22:31:30.431324

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.config import Settings


# revision identifiers, used by Alembic.
revision: str = '1927acae029d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# app settings
settings = Settings()


def upgrade() -> None:
    stmt = """
        INSERT INTO manufacturers (id, name, logo_url)
        VALUES 
        (1, 'Lenovo', 'https://upload.wikimedia.org/wikipedia/commons/c/c9/Lenovo_%282015%29.svg'),
        (2, 'Dell', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Dell_logo_2016.svg/1200px-Dell_logo_2016.svg.png'),
        (3, 'HP', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/HP_logo_2012.svg/1200px-HP_logo_2012.svg.png'),
        (4, 'Asus', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/ASUS_Logo.svg/2880px-ASUS_Logo.svg.png'),
        (5, 'Acer', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Acer_2011.svg/2880px-Acer_2011.svg.png'),
        (6, 'Apple', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/1920px-Apple_logo_black.svg.png'),
        (7, 'LG', 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/LG_logo_%282014%29.svg/2880px-LG_logo_%282014%29.svg.png'),
        (8, 'Toshiba', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Toshiba_logo.svg/2880px-Toshiba_logo.svg.png'),
        (9, 'Microsoft', 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Microsoft_logo_%282012%29.svg/2880px-Microsoft_logo_%282012%29.svg.png'),
        (10, 'Panasonic', 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Panasonic_logo_%28Blue%29.svg/2880px-Panasonic_logo_%28Blue%29.svg.png');
    """
    if "sqlite" not in settings.db_url:
        stmt.replace(";", "\nON CONFLICT (name) DO NOTHING;")

    op.execute(stmt)    


def downgrade() -> None:
    op.execute("""
        DELETE FROM products
        WHERE manufacturer_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
    """)

    op.execute("""
        DELETE FROM manufacturers 
        WHERE id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
    """)

