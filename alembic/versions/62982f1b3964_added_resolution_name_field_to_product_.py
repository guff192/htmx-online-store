"""Added resolution name field to product model

Revision ID: 62982f1b3964
Revises: eb5e9aecf603
Create Date: 2024-11-02 16:29:35.155404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62982f1b3964'
down_revision: Union[str, None] = 'eb5e9aecf603'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('products', sa.Column('resolution_name', sa.String(length=12), nullable=False, server_default=''))


def downgrade() -> None:
    op.drop_column('products', 'resolution_name')

