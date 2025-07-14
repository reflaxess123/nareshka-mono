"""add_user_profile_fields_manual

Revision ID: 9a819e455b7d
Revises: 8aa94f4d5a35
Create Date: 2025-07-14 10:43:05.996327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a819e455b7d'
down_revision = '8aa94f4d5a35'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем недостающие поля к таблице User
    op.add_column('User', sa.Column('username', sa.String(100), nullable=True))
    op.add_column('User', sa.Column('first_name', sa.String(100), nullable=True))
    op.add_column('User', sa.Column('last_name', sa.String(100), nullable=True))
    op.add_column('User', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('User', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))
    
    # Создаем индексы для новых полей
    op.create_index('idx_user_username', 'User', ['username'], unique=True)
    op.create_index('idx_user_email', 'User', ['email'], unique=True)


def downgrade() -> None:
    # Удаляем индексы
    op.drop_index('idx_user_email', table_name='User')
    op.drop_index('idx_user_username', table_name='User')
    
    # Удаляем добавленные поля
    op.drop_column('User', 'is_verified')
    op.drop_column('User', 'is_active')
    op.drop_column('User', 'last_name')
    op.drop_column('User', 'first_name')
    op.drop_column('User', 'username') 

