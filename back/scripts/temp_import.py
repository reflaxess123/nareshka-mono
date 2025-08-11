#!/usr/bin/env python3
"""
Импорт финальных категоризированных вопросов в базу данных
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Добавляем путь к корню проекта
sys.path.append(str(Path(__file__).parent.parent))

from app.core.settings import settings


def import_final_data():
    """Импорт финальных категоризированных данных в БД"""
    
    print("=" * 60)
    print("ИМПОРТ ФИНАЛЬНЫХ КАТЕГОРИЗИРОВАННЫХ ВОПРОСОВ")
    print("=" * 60)
    
    # Подключение к БД
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Путь к финальным данным
        data_path = Path(__file__).parent.parent.parent / "sobes-data" / "analysis" / "outputs_api_ready"
        
        # Загрузка финальных данных
        questions_file = data_path / "questions_full_final.json"
        categories_file = data_path / "categories_final.json"
        
        if not questions_file.exists():
            print(f"+ Файл с вопросами не найден: {questions_file}")
            return
            
        if not categories_file.exists():
            print(f"+ Файл с категориями не найден: {categories_file}")
            return
        
        # Загружаем данные
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
            
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories = json.load(f)
            
        print(f"+� Загружено {len(questions)} вопросов")
        print(f"+� Загружено {len(categories)} категорий")
        
        # Очистка старых данных
        print("\n+� Очистка старых данных...")
        session.execute(text("DELETE FROM interview_questions"))
        session.execute(text("DELETE FROM interview_categories"))
        session.commit()
        
        # Импорт категорий
        print("+� Импорт категорий...")
        for cat in categories:
            category_id = cat['name'].lower().replace(' ', '_').replace('ь', '').replace('ё', 'e')
            
            insert_query = text("""
                INSERT INTO interview_categories 
                (id, name, questions_count, clusters_count, percentage, color, icon)
                VALUES (:id, :name, :questions_count, :clusters_count, :percentage, :color, :icon)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    questions_count = EXCLUDED.questions_count,
                    clusters_count = EXCLUDED.clusters_count,
                    percentage = EXCLUDED.percentage,
                    color = EXCLUDED.color,
                    icon = EXCLUDED.icon
            """)
            
            # Определяем цвет и иконку по категории
            color_map = {
                'javascript_core': '#f7df1e',
                'react': '#61dafb', 
                'soft_skills': '#95a5a6',
                'typescript': '#3178c6',
                'set': '#e74c3c',
                'algoritmy': '#9b59b6',
                'verstka': '#e67e22',
                'instrumenty': '#34495e',
                'proizvoditelnost': '#27ae60',
                'testirovanie': '#16a085',
                'drugoe': '#7f8c8d',
                'arhitektura': '#8e44ad',
                'brauzery': '#2980b9'
            }
            
            icon_map = {
                'javascript_core': 'code',
                'react': 'react',
                'soft_skills': 'user',
                'typescript': 'typescript',
                'set': 'network',
                'algoritmy': 'algorithm',
                'verstka': 'layout',
                'instrumenty': 'tools',
                'proizvoditelnost': 'performance',
                'testirovanie': 'test',
                'drugoe': 'more',
                'arhitektura': 'architecture',
                'brauzery': 'browser'
            }
            
            session.execute(insert_query, {
                'id': category_id,
                'name': cat['name'],
                'questions_count': cat['questions_count'],
                'clusters_count': cat.get('clusters_count', 0),
                'percentage': cat['percentage'],
                'color': color_map.get(category_id, '#95a5a6'),
                'icon': icon_map.get(category_id, 'question')
            })
        
        session.commit()
        print(f"+ Импортировано {len(categories)} категорий")
        
        # Импорт вопросов батчами
        print("+� Импорт вопросов...")
        batch_size = 1000
        
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i + batch_size]
            
            for q in batch:
                category_id = None
                if q.get('category'):
                    category_id = q['category'].lower().replace(' ', '_').replace('ь', '').replace('ё', 'e')
                
                # Парсим дату
                try:
                    date_obj = datetime.strptime(q['date'], '%Y-%m-%d') if q.get('date') else None
                except:
                    date_obj = None
                
                insert_query = text("""
                    INSERT INTO interview_questions 
                    (id, question_text, company, interview_date, category_id, topic, cluster_id, canonical_question)
                    VALUES (:id, :question_text, :company, :interview_date, :category_id, :topic, :cluster_id, :canonical_question)
                    ON CONFLICT (id) DO UPDATE SET
                        question_text = EXCLUDED.question_text,
                        company = EXCLUDED.company,
                        interview_date = EXCLUDED.interview_date,
                        category_id = EXCLUDED.category_id,
                        topic = EXCLUDED.topic,
                        cluster_id = EXCLUDED.cluster_id,
                        canonical_question = EXCLUDED.canonical_question
                """)
                
                session.execute(insert_query, {
                    'id': q['id'],
                    'question_text': q['question'],
                    'company': q.get('company'),
                    'interview_date': date_obj,
                    'category_id': category_id,
                    'topic': q.get('topic'),
                    'cluster_id': q.get('cluster_id'),
                    'canonical_question': q.get('canonical_question')
                })
            
            session.commit()
            print(f"  + Обработано {min(i + batch_size, len(questions))}/{len(questions)} вопросов")
        
        print(f"\n+� ИМПОРТ ЗАВЕРШЕН!")
        print(f"+� Статистика:")
        print(f"   Категории: {len(categories)}")
        print(f"   Вопросы: {len(questions)}")
        
        # Проверка результата
        result = session.execute(text("SELECT COUNT(*) FROM interview_categories")).scalar()
        print(f"   В БД категорий: {result}")
        
        result = session.execute(text("SELECT COUNT(*) FROM interview_questions")).scalar()
        print(f"   В БД вопросов: {result}")
        
        # Статистика по категориям
        print(f"\n+� Распределение по категориям в БД:")
        results = session.execute(text("""
            SELECT c.name, COUNT(q.id) as count 
            FROM interview_categories c 
            LEFT JOIN interview_questions q ON c.id = q.category_id 
            GROUP BY c.id, c.name 
            ORDER BY count DESC
        """)).fetchall()
        
        for name, count in results[:10]:
            print(f"   {name}: {count}")
            
    except Exception as e:
        print(f"+ Ошибка импорта: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import_final_data()