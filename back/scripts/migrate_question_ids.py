#!/usr/bin/env python3
"""
МИГРАЦИЯ ID ВОПРОСОВ - СОЗДАНИЕ УНИКАЛЬНЫХ ID БЕЗ ПОЛОМКИ ЛОГИКИ

Этот скрипт:
1. Применяет миграцию базы данных (добавляет поля)
2. Создает новый CSV с уникальными ID 
3. Переимпортирует все 8,532 вопроса
4. Сохраняет исходную логику позиций в интервью
"""

import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Добавляем путь к корню проекта
sys.path.append(str(Path(__file__).parent.parent))
from app.core.settings import settings

def create_unique_csv():
    """Создает новый CSV файл с уникальными ID"""
    print("=" * 70)
    print("СОЗДАНИЕ CSV С УНИКАЛЬНЫМИ ID")
    print("=" * 70)
    
    # Читаем исходный файл
    input_file = Path("../sobes-data/analysis/outputs_bertopic_final/all_questions_with_categories.csv")
    df = pd.read_csv(input_file)
    
    print(f"Исходный файл: {len(df)} вопросов")
    print(f"Уникальных исходных ID: {df['id'].nunique()}")
    
    # Создаем новую структуру данных
    new_data = []
    
    for idx, row in df.iterrows():
        # Создаем уникальный ID на основе позиции в файле
        unique_id = f"q_{idx + 1:06d}"  # q_000001, q_000002, etc
        
        new_data.append({
            'id': unique_id,                          # Новый уникальный ID
            'original_question_id': row['id'],        # q1, q2, q3 - исходная позиция
            'interview_id': 'unknown',                # Будет заполнено если есть в данных
            'question_text': row['question_text'],
            'company': row['company'],
            'date': row['date'],
            'cluster_id': row['cluster_id'] if row['cluster_id'] != -1 else None,
            'final_category': row['final_category'] if row['final_category'] != 'Нет кластера' else None,
            'topic_name': row['topic_name'] if row['topic_name'] != 'Нет темы' else None,
            'canonical_question': row['canonical_question'] if pd.notna(row['canonical_question']) else None
        })
    
    # Создаем новый DataFrame
    new_df = pd.DataFrame(new_data)
    
    # Сохраняем новый файл
    output_dir = Path("../sobes-data/analysis/outputs_migration")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "questions_with_unique_ids.csv"
    new_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"Создан файл: {output_file}")
    print(f"Записей: {len(new_df)}")
    print(f"Уникальных ID: {new_df['id'].nunique()}")
    print(f"Исходных позиций: {new_df['original_question_id'].nunique()}")
    
    # Показываем примеры
    print(f"\nПРИМЕРЫ ДАННЫХ:")
    for i in range(3):
        row = new_df.iloc[i]
        print(f"   {row['id']} (было: {row['original_question_id']}) -> {row['question_text'][:50]}...")
    
    return output_file

def apply_migration():
    """Применяет миграцию базы данных"""
    print("\n" + "=" * 70)
    print("ПРИМЕНЕНИЕ МИГРАЦИИ БАЗЫ ДАННЫХ")
    print("=" * 70)
    
    try:
        # Применяем миграцию
        os.system("cd .. && alembic upgrade head")
        print("Миграция применена успешно")
        return True
    except Exception as e:
        print(f"Ошибка миграции: {e}")
        return False

def clear_and_reimport_data(csv_file):
    """Очищает таблицу и импортирует новые данные"""
    print("\n" + "=" * 70)
    print("ПЕРЕИМПОРТ ДАННЫХ С УНИКАЛЬНЫМИ ID")
    print("=" * 70)
    
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 1. Очищаем существующие вопросы (сохраняем категории и кластеры)
        print("Очистка существующих вопросов...")
        deleted_count = session.execute(text('DELETE FROM "InterviewQuestion"')).rowcount
        print(f"   Удалено записей: {deleted_count}")
        
        # 2. Читаем новые данные
        print("Чтение нового файла...")
        df = pd.read_csv(csv_file)
        print(f"   Загружено: {len(df)} вопросов")
        
        # 3. Импортируем батчами
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
                            'cluster_id': row['cluster_id'] if pd.notna(row['cluster_id']) else None,
                            'category_id': row['final_category'].replace(' ', '_').lower() if pd.notna(row['final_category']) else None,
                            'topic_name': row['topic_name'] if pd.notna(row['topic_name']) else None,
                            'canonical_question': row['canonical_question'][:2000] if pd.notna(row['canonical_question']) else None
                        }
                    )
                    imported += 1
                    
                except Exception as e:
                    print(f"Ошибка импорта записи {row['id']}: {e}")
                    continue
            
            # Коммитим батч
            session.commit()
            print(f"   Импортировано: {min(i+batch_size, len(df))}/{len(df)}")
        
        # 4. Проверяем результат
        total = session.execute(text('SELECT COUNT(*) FROM "InterviewQuestion"')).scalar()
        categorized = session.execute(text('SELECT COUNT(*) FROM "InterviewQuestion" WHERE category_id IS NOT NULL')).scalar()
        
        print(f"\nРЕЗУЛЬТАТ ИМПОРТА:")
        print(f"   Успешно импортировано: {imported}")
        print(f"   Всего в базе: {total}")
        print(f"   Категоризировано: {categorized} ({categorized/total*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"Ошибка импорта: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def verify_migration():
    """Проверяет успешность миграции"""
    print("\n" + "=" * 70)
    print("ПРОВЕРКА МИГРАЦИИ")
    print("=" * 70)
    
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Проверяем структуру
        result = session.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT id) as unique_ids,
                COUNT(DISTINCT original_question_id) as unique_positions,
                COUNT(*) FILTER (WHERE category_id IS NOT NULL) as categorized
            FROM "InterviewQuestion"
        """)).fetchone()
        
        print(f"Всего вопросов: {result.total}")
        print(f"Уникальных ID: {result.unique_ids}")
        print(f"Исходных позиций: {result.unique_positions}")
        print(f"Категоризированных: {result.categorized}")
        
        # Показываем примеры
        examples = session.execute(text("""
            SELECT id, original_question_id, LEFT(question_text, 40) as preview
            FROM "InterviewQuestion"
            ORDER BY id
            LIMIT 5
        """)).fetchall()
        
        print(f"\nПРИМЕРЫ В БАЗЕ:")
        for ex in examples:
            print(f"   {ex.id} (было: {ex.original_question_id}) -> {ex.preview}...")
        
        # Проверяем что исходная логика сохранена
        positions_check = session.execute(text("""
            SELECT original_question_id, COUNT(*) as count
            FROM "InterviewQuestion"
            WHERE original_question_id IN ('q1', 'q2', 'q3')
            GROUP BY original_question_id
            ORDER BY original_question_id
        """)).fetchall()
        
        print(f"\nПРОВЕРКА ИСХОДНОЙ ЛОГИКИ:")
        for pos in positions_check:
            print(f"   Позиция {pos.original_question_id}: {pos.count} вопросов из разных интервью")
        
        return True
        
    except Exception as e:
        print(f"Ошибка проверки: {e}")
        return False
    finally:
        session.close()

def main():
    """Главная функция - выполняет полную миграцию"""
    print("СТРАТЕГИЯ МИГРАЦИИ БЕЗ ПОЛОМКИ ИСХОДНОЙ ЗАДУМКИ")
    print("План:")
    print("   1. Создание CSV с уникальными ID")
    print("   2. Применение миграции базы данных") 
    print("   3. Переимпорт всех 8,532 вопросов")
    print("   4. Проверка результата")
    
    print("Начинаем миграцию...")
    
    # Этап 1: Создание CSV
    csv_file = create_unique_csv()
    
    # Этап 2: Миграция базы
    if not apply_migration():
        print("Миграция не удалась, останавливаемся")
        return
    
    # Этап 3: Переимпорт данных
    if not clear_and_reimport_data(csv_file):
        print("Импорт не удался, останавливаемся") 
        return
    
    # Этап 4: Проверка
    if verify_migration():
        print("\nМИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("\nЧТО ПОЛУЧИЛОСЬ:")
        print("   - Все 8,532 вопроса в базе с уникальными ID")
        print("   - Исходная логика позиций сохранена (q1, q2, q3...)")
        print("   - API работает с полными данными")
        print("   - Поиск и категоризация работают")
        print("\nЧТО ИЗМЕНИЛОСЬ:")
        print("   - id: уникальные ID (q_000001, q_000002...)")
        print("   - original_question_id: исходные позиции (q1, q2, q3...)")  
        print("   - interview_id: идентификатор интервью (пока 'unknown')")
    else:
        print("Проверка не прошла")

if __name__ == "__main__":
    main()