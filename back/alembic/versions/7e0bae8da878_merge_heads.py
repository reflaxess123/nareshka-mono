"""merge_heads

Revision ID: 7e0bae8da878
Revises: 20250730_add_interview_tables, 9a819e455b7d
Create Date: 2025-07-30 21:17:36.656988

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e0bae8da878'
down_revision = ('20250730_add_interview_tables', '9a819e455b7d')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 