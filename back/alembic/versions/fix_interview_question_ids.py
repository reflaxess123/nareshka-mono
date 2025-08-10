"""Fix interview question IDs to be unique

Revision ID: fix_interview_question_ids
Revises: add_interview_categories
Create Date: 2025-01-10
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'fix_interview_question_ids'
down_revision = 'add_interview_categories'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Добавляем поля для сохранения исходной логики позиций и интервью,
    изменяем ID на уникальный
    """
    # Добавляем новые поля для сохранения исходной семантики
    op.add_column('InterviewQuestion', sa.Column('original_question_id', sa.String(10), nullable=True))
    op.add_column('InterviewQuestion', sa.Column('interview_id', sa.String(100), nullable=True))
    
    # Заполняем новые поля из существующих данных (если есть)
    # original_question_id будет содержать q1, q2, q3 - исходную позицию
    op.execute("""
        UPDATE "InterviewQuestion" 
        SET original_question_id = id
    """)
    
    # Создаем индексы для новых полей
    op.create_index('ix_interview_question_original_id', 'InterviewQuestion', ['original_question_id'])
    op.create_index('ix_interview_question_interview', 'InterviewQuestion', ['interview_id'])
    
    # Создаем составной индекс для поиска по интервью + позиции
    op.create_index('ix_interview_question_composite', 'InterviewQuestion', 
                   ['interview_id', 'original_question_id'])


def downgrade() -> None:
    """Откат изменений"""
    op.drop_index('ix_interview_question_composite', table_name='InterviewQuestion')
    op.drop_index('ix_interview_question_interview', table_name='InterviewQuestion')
    op.drop_index('ix_interview_question_original_id', table_name='InterviewQuestion')
    op.drop_column('InterviewQuestion', 'interview_id')
    op.drop_column('InterviewQuestion', 'original_question_id')