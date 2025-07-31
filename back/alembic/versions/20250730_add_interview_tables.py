"""add_interview_tables

Revision ID: 20250730_add_interview_tables
Revises: 8aa94f4d5a35
Create Date: 2025-07-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20250730_add_interview_tables'
down_revision = '8aa94f4d5a35'  # Последняя миграция
branch_labels = None
depends_on = None

def upgrade():
    # Создание таблицы InterviewRecord
    op.create_table('InterviewRecord',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_name', sa.String(), nullable=False),
        sa.Column('interview_date', sa.DateTime(), nullable=False),
        sa.Column('stage_number', sa.Integer(), nullable=True),
        sa.Column('position', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('full_content', sa.Text(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('questions_count', sa.Integer(), nullable=True),
        sa.Column('technologies', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('difficulty_level', sa.Integer(), nullable=True),
        sa.Column('telegram_author', sa.String(), nullable=True),
        sa.Column('source_type', sa.String(), nullable=True, server_default='telegram'),
        sa.Column('content_hash', sa.String(), nullable=True),
        sa.Column('extracted_urls', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('companies', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updatedAt', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Создание таблицы InterviewAnalytics
    op.create_table('InterviewAnalytics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('metric_type', sa.String(), nullable=False),
        sa.Column('metric_value', sa.String(), nullable=False),
        sa.Column('period', sa.String(), nullable=True),
        sa.Column('total_interviews', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_difficulty', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('avg_duration', sa.Integer(), nullable=True),
        sa.Column('common_questions', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('additional_data', postgresql.JSONB(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(), nullable=False),
        sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updatedAt', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Создание индексов
    op.create_index('idx_interview_companies', 'InterviewRecord', ['companies'], postgresql_using='gin')
    op.create_index('idx_interview_technologies', 'InterviewRecord', ['technologies'], postgresql_using='gin')
    op.create_index('idx_interview_tags', 'InterviewRecord', ['tags'], postgresql_using='gin')
    op.create_index('idx_interview_date', 'InterviewRecord', ['interview_date'])
    op.create_index('idx_interview_company_name', 'InterviewRecord', ['company_name'])
    op.create_index('idx_interview_stage', 'InterviewRecord', ['stage_number'])
    op.create_index('idx_analytics_type_value', 'InterviewAnalytics', ['metric_type', 'metric_value'])

def downgrade():
    # Удаление индексов
    op.drop_index('idx_analytics_type_value', table_name='InterviewAnalytics')
    op.drop_index('idx_interview_stage', table_name='InterviewRecord')
    op.drop_index('idx_interview_company_name', table_name='InterviewRecord')
    op.drop_index('idx_interview_date', table_name='InterviewRecord')
    op.drop_index('idx_interview_tags', table_name='InterviewRecord')
    op.drop_index('idx_interview_technologies', table_name='InterviewRecord')
    op.drop_index('idx_interview_companies', table_name='InterviewRecord')
    
    # Удаление таблиц
    op.drop_table('InterviewAnalytics')
    op.drop_table('InterviewRecord')