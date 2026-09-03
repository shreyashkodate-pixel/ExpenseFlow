"""email_verification_otps

Revision ID: 9c1a2b3d4e5f
Revises: 8b9f0e2a3c4d
Create Date: 2026-09-03 15:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c1a2b3d4e5f'
down_revision: Union[str, None] = '8b9f0e2a3c4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'email_verification_otps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('otp_hash', sa.String(length=64), nullable=False),
        sa.Column('verification_token_hash', sa.String(length=64), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_verification_otps_id'), 'email_verification_otps', ['id'], unique=False)
    op.create_index(op.f('ix_email_verification_otps_email'), 'email_verification_otps', ['email'], unique=False)
    op.create_index(op.f('ix_email_verification_otps_verification_token_hash'), 'email_verification_otps', ['verification_token_hash'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_email_verification_otps_verification_token_hash'), table_name='email_verification_otps')
    op.drop_index(op.f('ix_email_verification_otps_email'), table_name='email_verification_otps')
    op.drop_index(op.f('ix_email_verification_otps_id'), table_name='email_verification_otps')
    op.drop_table('email_verification_otps')
