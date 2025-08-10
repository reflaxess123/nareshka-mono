#!/usr/bin/env python3
"""
Импорт данных с уникальными ID после применения миграции
"""
import pandas as pd
import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Добавляем путь к корню проекта
sys.path.append(str(Path(__file__).parent.parent))
from app.core.settings import settings

def main():
    print("ИМПОРТ ДАННЫХ С УНИКАЛЬНЫМИ ID")
    print("=" * 50)
    
    # Читаем созданный CSV файл
    csv_file = Path("../sobes-data/analysis/outputs_migration/questions_with_unique_ids.csv")
    
    if not csv_file.exists():
        print(f"Ошибка: файл {csv_file} не найден")
        print("Сначала запустите создание CSV файла")
        return
    
    df = pd.read_csv(csv_file)
    print(f"Загружено: {len(df)} вопросов")
    
    # Подключение к БД
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Очищаем существующие вопросы
        print("Очистка существующих вопросов...")
        deleted = session.execute(text('DELETE FROM "InterviewQuestion"')).rowcount
        print(f"Удалено: {deleted} записей")
        
        # Импортируем новые данные
        imported = 0
        batch_size = 500
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                try:
                    session.execute(
                        text("""
                            INSERT INTO "InterviewQuestion"
                            (id, original_question_id, interview_id, question_text, company, 
                             cluster_id, category_id, topic_name, canonical_question)
                            VALUES (:id, :original_question_id, :interview_id, :question_text, 
                                   :company, :cluster_id, :category_id, :topic_name, :canonical_question)
                        """),
                        {
                            'id': row['id'],
                            'original_question_id': row['original_question_id'],
                            'interview_id': row['interview_id'],
                            'question_text': row['question_text'][:2000],
                            'company': row['company'] if pd.notna(row['company']) else None,
                            'cluster_id': int(row['cluster_id']) if pd.notna(row['cluster_id']) else None,
                            'category_id': row['final_category'].replace(' ', '_').lower() if pd.notna(row['final_category']) else None,
                            'topic_name': row['topic_name'] if pd.notna(row['topic_name']) else None,
                            'canonical_question': row['canonical_question'][:2000] if pd.notna(row['canonical_question']) else None
                        }
                    )
                    imported += 1
                    
                except Exception as e:
                    print(f"Ошибка импорта {row['id']}: {e}")
                    continue
            
            session.commit()
            print(f"Импортировано: {min(i+batch_size, len(df))}/{len(df)}")
        
        # Проверяем результат
        total = session.execute(text('SELECT COUNT(*) FROM "InterviewQuestion"')).scalar()
        categorized = session.execute(text('SELECT COUNT(*) FROM "InterviewQuestion" WHERE category_id IS NOT NULL')).scalar()
        
        print(f"\nРЕЗУЛЬТАТ:")
        print(f"Импортировано: {imported}")
        print(f"Всего в базе: {total}")
        print(f"Категоризировано: {categorized} ({categorized/total*100:.1f}%)")
        
        # Примеры
        examples = session.execute(text("""
            SELECT id, original_question_id, LEFT(question_text, 50) as preview
            FROM "InterviewQuestion"
            ORDER BY id
            LIMIT 5
        """)).fetchall()
        
        print(f"\nПРИМЕРЫ В БАЗЕ:")
        for ex in examples:
            print(f"   {ex.id} (было: {ex.original_question_id}) -> {ex.preview}...")
        
        print(f"\nУСПЕШНО! Теперь у вас {total} вопросов с уникальными ID в базе!")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()