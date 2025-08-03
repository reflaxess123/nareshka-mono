"""
Миграция для добавления поля has_audio_recording в таблицу InterviewRecord
"""

import sys
import os
from sqlalchemy import text

# Добавляем путь к app в PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.shared.database import get_session


def add_audio_recording_field():
    """Добавляет поле has_audio_recording в таблицу InterviewRecord"""
    session = next(get_session())
    
    try:
        # Обновляем существующие LLM-отчеты
        result = session.execute(text('''
            UPDATE "InterviewRecord" 
            SET has_audio_recording = TRUE 
            WHERE source_type = 'llm_report'
        '''))
        
        session.commit()
        print(f"SUCCESS: Обновлено {result.rowcount} LLM-отчетов")
        print("SUCCESS: LLM-отчеты помечены как имеющие аудио/видеозапись")
        
    except Exception as e:
        print(f"ERROR: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    add_audio_recording_field()