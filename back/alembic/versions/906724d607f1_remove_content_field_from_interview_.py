"""remove_content_field_from_interview_record

Revision ID: 906724d607f1
Revises: 7e0bae8da878
Create Date: 2025-08-02 11:13:49.099804

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '906724d607f1'
down_revision = '7e0bae8da878'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove the content column from InterviewRecord table
    op.drop_column('InterviewRecord', 'content')


def downgrade() -> None:
    # Add back the content column if needed to rollback
    op.add_column('InterviewRecord', sa.Column('content', sa.Text(), nullable=False, server_default='')) 