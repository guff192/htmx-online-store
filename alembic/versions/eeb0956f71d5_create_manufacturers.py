"""Create manufacturers

Revision ID: eeb0956f71d5
Revises: 34ad3db6e07f
Create Date: 2024-10-30 01:04:47.426798

"""
from typing import Sequence, Union

from alembic import op

from app.config import Settings


# revision identifiers, used by Alembic.
revision: str = 'eeb0956f71d5'
down_revision: Union[str, None] = '34ad3db6e07f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


settings = Settings()


def upgrade() -> None:
    stmt = """
        INSERT INTO manufacturers (name, logo_url)
        VALUES 
        ('Lenovo', 'https://upload.wikimedia.org/wikipedia/commons/c/c9/Lenovo_%282015%29.svg'),
        ('Dell', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Dell_logo_2016.svg/1200px-Dell_logo_2016.svg.png'),
        ('HP', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/HP_logo_2012.svg/1200px-HP_logo_2012.svg.png'),
        ('Asus', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/ASUS_Logo.svg/2880px-ASUS_Logo.svg.png'),
        ('Acer', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Acer_2011.svg/2880px-Acer_2011.svg.png'),
        ('Apple', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/1920px-Apple_logo_black.svg.png'),
        ('LG', 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/LG_logo_%282014%29.svg/2880px-LG_logo_%282014%29.svg.png'),
        ('Toshiba', 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Toshiba_logo.svg/2880px-Toshiba_logo.svg.png'),
        ('Microsoft', 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Microsoft_logo_%282012%29.svg/2880px-Microsoft_logo_%282012%29.svg.png');
    """
    if "sqlite" not in settings.db_url:
        stmt.replace(";", "\nON CONFLICT (name) DO NOTHING;")

    op.execute(stmt)    


def downgrade() -> None:
    op.execute("""
        DELETE FROM manufacturers 
        WHERE name IN ('Lenovo', 'Dell', 'HP');
    """)

