"""Add manufacturers

Revision ID: c77e2efc9311
Revises: 27bcc1d2d167
Create Date: 2024-10-29 19:09:25.382368

"""
from typing import Sequence, Union

from alembic import op

from app.config import Settings


# revision identifiers, used by Alembic.
revision: str = 'c77e2efc9311'
down_revision: Union[str, None] = '27bcc1d2d167'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


settings = Settings()


def upgrade() -> None:
    stmt = """
        INSERT INTO manufacturers (name, logo_url)
        VALUES 
        ('Lenovo', 'https://upload.wikimedia.org/wikipedia/commons/c/c9/Lenovo_%282015%29.svg'),
        ('Dell', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Dell_logo_2016.svg/1200px-Dell_logo_2016.svg.png'),
        ('HP', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/HP_logo_2012.svg/1200px-HP_logo_2012.svg.png');
    """
    if "sqlite" not in settings.db_url:
        stmt.replace(";", "\nON CONFLICT (name) DO NOTHING;")

    op.execute(stmt)    


def downgrade() -> None:
    op.execute("""
        DELETE FROM manufacturers 
        WHERE name IN ('Lenovo', 'Dell', 'HP');
    """)

