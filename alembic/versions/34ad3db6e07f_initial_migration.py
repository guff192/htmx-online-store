"""Initial migration

Revision ID: 34ad3db6e07f
Revises: 
Create Date: 2024-10-30 00:55:11.311573

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '34ad3db6e07f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'banners',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('img_url', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True
    )
    op.create_index(op.f('ix_banners_id'), 'banners', ['id'], unique=False, if_not_exists=True)
    op.create_index(op.f('ix_banners_name'), 'banners', ['name'], unique=True, if_not_exists=True)

    op.create_table(
        'manufacturers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('logo_url', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        if_not_exists=True
    )
    op.create_index(op.f('ix_manufacturers_id'), 'manufacturers', ['id'], unique=False, if_not_exists=True)

    op.create_table(
        'product_configurations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ram_amount', sa.Integer(), nullable=False),
        sa.Column('ssd_amount', sa.Integer(), nullable=False),
        sa.Column('additional_price', sa.Integer(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('additional_ram', sa.Boolean(), nullable=False),
        sa.Column('soldered_ram', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True
    )
    op.create_index(op.f('ix_product_configurations_id'), 'product_configurations', ['id'], unique=False, if_not_exists=True)

    op.create_table(
        'users',
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column('google_id', sa.String(length=21), nullable=True),
        sa.Column('yandex_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sqlalchemy_utils.types.email.EmailType(length=255), nullable=True),
        sa.Column('phone', sa.String(length=255), nullable=True),
        sa.Column('profile_img_url', sa.String(length=255), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_id'),
        sa.UniqueConstraint('phone'),
        sa.UniqueConstraint('yandex_id'),
        if_not_exists=True
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False, if_not_exists=True)

    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('comment', sa.String(length=255), nullable=False),
        sa.Column('buyer_name', sa.String(length=255), nullable=False),
        sa.Column('buyer_phone', sa.String(length=255), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=True),
        sa.Column('region_name', sa.String(length=255), nullable=True),
        sa.Column('city_id', sa.Integer(), nullable=True),
        sa.Column('city_name', sa.String(length=255), nullable=True),
        sa.Column('delivery_address', sa.String(length=255), nullable=False),
        sa.Column('delivery_track_number', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False, if_not_exists=True)

    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('price', sa.Integer(), nullable=True),
        sa.Column('count', sa.Integer(), nullable=True),
        sa.Column('newcomer', sa.Boolean(), nullable=False),
        sa.Column('manufacturer_id', sa.Integer(), nullable=True),
        sa.Column('soldered_ram', sa.Integer(), nullable=False),
        sa.Column('can_add_ram', sa.Boolean(), nullable=False),
        sa.Column('resolution', sa.String(length=10), nullable=False),
        sa.Column('cpu', sa.String(length=12), nullable=False),
        sa.Column('gpu', sa.String(length=12), nullable=False),
        sa.Column('touch_screen', sa.Boolean(), nullable=False),
        sa.Column('default_configuration_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['default_configuration_id'], ['product_configurations.id'], ),
        sa.ForeignKeyConstraint(['manufacturer_id'], ['manufacturers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False, if_not_exists=True)
    op.create_index(op.f('ix_products_name'), 'products', ['name'], unique=True, if_not_exists=True)

    op.create_table(
        'available_product_configurations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('configuration_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['configuration_id'], ['product_configurations.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True
    )
    op.create_index(op.f('ix_available_product_configurations_id'), 'available_product_configurations', ['id'], unique=False, if_not_exists=True)

    op.create_table(
        'order_products',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('selected_configuration_id', sa.Integer(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['selected_configuration_id'], ['product_configurations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True
    )
    op.create_index(op.f('ix_order_products_id'), 'order_products', ['id'], unique=False, if_not_exists=True)

    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=31), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True
    )
    op.create_index(op.f('ix_payments_date'), 'payments', ['date'], unique=False, if_not_exists=True)
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False, if_not_exists=True)
    op.create_index(op.f('ix_payments_status'), 'payments', ['status'], unique=False, if_not_exists=True)

    op.create_table(
        'user_products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('selected_configuration_id', sa.Integer(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['selected_configuration_id'], ['product_configurations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True
    )
    op.create_index(op.f('ix_user_products_id'), 'user_products', ['id'], unique=False, if_not_exists=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_products_id'), table_name='user_products')
    op.drop_table('user_products')
    op.drop_index(op.f('ix_payments_status'), table_name='payments')
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_date'), table_name='payments')
    op.drop_table('payments')
    op.drop_index(op.f('ix_order_products_id'), table_name='order_products')
    op.drop_table('order_products')
    op.drop_index(op.f('ix_available_product_configurations_id'), table_name='available_product_configurations')
    op.drop_table('available_product_configurations')
    op.drop_index(op.f('ix_products_name'), table_name='products')
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.drop_table('products')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_product_configurations_id'), table_name='product_configurations')
    op.drop_table('product_configurations')
    op.drop_index(op.f('ix_manufacturers_id'), table_name='manufacturers')
    op.drop_table('manufacturers')
    op.drop_index(op.f('ix_banners_name'), table_name='banners')
    op.drop_index(op.f('ix_banners_id'), table_name='banners')
    op.drop_table('banners')

