"""Add interview categories and clusters tables

Revision ID: add_interview_categories
Revises: 2450_24-12-17_15-26-18
Create Date: 2025-01-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_interview_categories'
down_revision = 'b025597888a1'  # Последняя существующая миграция
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем таблицу категорий
    op.create_table('InterviewCategory',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('questions_count', sa.Integer(), nullable=False),
        sa.Column('clusters_count', sa.Integer(), nullable=False),
        sa.Column('percentage', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updatedAt', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Создаем таблицу кластеров/топиков
    op.create_table('InterviewCluster',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category_id', sa.String(), nullable=False),
        sa.Column('keywords', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('questions_count', sa.Integer(), nullable=False),
        sa.Column('example_question', sa.Text(), nullable=True),
        sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updatedAt', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['category_id'], ['InterviewCategory.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаем таблицу вопросов с категоризацией
    op.create_table('InterviewQuestion',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('company', sa.String(), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('cluster_id', sa.Integer(), nullable=True),
        sa.Column('category_id', sa.String(), nullable=True),
        sa.Column('topic_name', sa.String(), nullable=True),
        sa.Column('canonical_question', sa.Text(), nullable=True),
        sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updatedAt', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['category_id'], ['InterviewCategory.id'], ),
        sa.ForeignKeyConstraint(['cluster_id'], ['InterviewCluster.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Добавляем индексы для производительности
    op.create_index('ix_interview_question_category', 'InterviewQuestion', ['category_id'])
    op.create_index('ix_interview_question_cluster', 'InterviewQuestion', ['cluster_id'])
    op.create_index('ix_interview_question_company', 'InterviewQuestion', ['company'])
    op.create_index('ix_interview_cluster_category', 'InterviewCluster', ['category_id'])


def downgrade() -> None:
    op.drop_index('ix_interview_cluster_category', table_name='InterviewCluster')
    op.drop_index('ix_interview_question_company', table_name='InterviewQuestion')
    op.drop_index('ix_interview_question_cluster', table_name='InterviewQuestion')
    op.drop_index('ix_interview_question_category', table_name='InterviewQuestion')
    op.drop_table('InterviewQuestion')
    op.drop_table('InterviewCluster')
    op.drop_table('InterviewCategory')