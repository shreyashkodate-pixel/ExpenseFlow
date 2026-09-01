"""auth_and_user_isolation

Revision ID: 7a8e9f1b2c3d
Revises: 48cef29c36e8
Create Date: 2026-08-31 19:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a8e9f1b2c3d'
down_revision: Union[str, None] = '48cef29c36e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('google_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_google_id'), 'users', ['google_id'], unique=True)

    # 2. Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('device_info', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_tokens_id'), 'refresh_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=True)
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False)

    # 3. Create password_reset_tokens table
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_password_reset_tokens_id'), 'password_reset_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_password_reset_tokens_token_hash'), 'password_reset_tokens', ['token_hash'], unique=True)
    op.create_index(op.f('ix_password_reset_tokens_user_id'), 'password_reset_tokens', ['user_id'], unique=False)

    # 4. Update categories table (add user_id, make name non-unique globally)
    op.add_column('categories', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_categories_user_id', 'categories', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_categories_user_id'), 'categories', ['user_id'], unique=False)
    op.drop_index('ix_categories_name', table_name='categories')
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=False)

    # 5. Update expenses table (add user_id)
    op.add_column('expenses', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_expenses_user_id', 'expenses', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_expenses_user_id'), 'expenses', ['user_id'], unique=False)

    # 6. Update budgets table (add user_id)
    op.add_column('budgets', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_budgets_user_id', 'budgets', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_budgets_user_id'), 'budgets', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_budgets_user_id'), table_name='budgets')
    op.drop_constraint('fk_budgets_user_id', 'budgets', type_='foreignkey')
    op.drop_column('budgets', 'user_id')

    op.drop_index(op.f('ix_expenses_user_id'), table_name='expenses')
    op.drop_constraint('fk_expenses_user_id', 'expenses', type_='foreignkey')
    op.drop_column('expenses', 'user_id')

    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.create_index('ix_categories_name', 'categories', ['name'], unique=True)
    op.drop_index(op.f('ix_categories_user_id'), table_name='categories')
    op.drop_constraint('fk_categories_user_id', 'categories', type_='foreignkey')
    op.drop_column('categories', 'user_id')

    op.drop_index(op.f('ix_password_reset_tokens_user_id'), table_name='password_reset_tokens')
    op.drop_index(op.f('ix_password_reset_tokens_token_hash'), table_name='password_reset_tokens')
    op.drop_index(op.f('ix_password_reset_tokens_id'), table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')

    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_token_hash'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_id'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')

    op.drop_index(op.f('ix_users_google_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
