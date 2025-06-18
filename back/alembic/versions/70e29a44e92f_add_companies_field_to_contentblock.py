"""add companies field to ContentBlock

Revision ID: 70e29a44e92f
Revises: 42c1e4093aa2
Create Date: 2025-06-18 11:32:05.537229

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '70e29a44e92f'
down_revision = '42c1e4093aa2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('ContentBlock', sa.Column('companies', postgresql.ARRAY(sa.String()), server_default='{}', nullable=False))


def downgrade() -> None:
    op.drop_column('ContentBlock', 'companies') 