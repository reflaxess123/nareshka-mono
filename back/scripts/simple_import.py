#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Добавляем путь к корню проекта
sys.path.append(str(Path(__file__).parent.parent))

from app.core.settings import settings

def main():
    print("Importing final categorized data...")
    
    # Подключение к БД
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Путь к данным
        data_path = Path(__file__).parent.parent.parent / "sobes-data" / "analysis" / "outputs_api_ready"
        
        # Загрузка данных
        with open(data_path / "questions_full_final.json", 'r', encoding='utf-8') as f:
            questions = json.load(f)
        with open(data_path / "categories_final.json", 'r', encoding='utf-8') as f:
            categories = json.load(f)
        
        print(f"Loaded {len(questions)} questions and {len(categories)} categories")
        
        # Очистка (в правильном порядке из-за FK constraints)
        session.execute(text('DELETE FROM "InterviewQuestion"'))
        session.execute(text('DELETE FROM "InterviewCluster"'))  
        session.execute(text('DELETE FROM "InterviewCategory"'))
        session.commit()
        print("Cleared old data")
        
        # Импорт категорий
        for cat in categories:
            category_id = cat['name'].lower().replace(' ', '_').replace('ь', '').replace('ё', 'e')
            
            session.execute(text("""
                INSERT INTO "InterviewCategory" 
                (id, name, questions_count, clusters_count, percentage, color, icon)
                VALUES (:id, :name, :questions_count, :clusters_count, :percentage, :color, :icon)
            """), {
                'id': category_id,
                'name': cat['name'],
                'questions_count': cat['questions_count'],
                'clusters_count': cat.get('clusters_count', 0),
                'percentage': cat['percentage'],
                'color': '#95a5a6',
                'icon': 'question'
            })
        
        session.commit()
        print(f"Imported {len(categories)} categories")
        
        # Импорт вопросов
        batch_size = 1000
        question_counter = 1
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i + batch_size]
            
            for q in batch:
                category_id = None
                if q.get('category'):
                    category_id = q['category'].lower().replace(' ', '_').replace('ь', '').replace('ё', 'e')
                
                try:
                    date_obj = datetime.strptime(q['date'], '%Y-%m-%d') if q.get('date') else None
                except:
                    date_obj = None
                
                session.execute(text("""
                    INSERT INTO "InterviewQuestion" 
                    (id, question_text, company, date, category_id, topic_name, canonical_question)
                    VALUES (:id, :question_text, :company, :date, :category_id, :topic_name, :canonical_question)
                """), {
                    'id': f"q{question_counter}",
                    'question_text': q['question'],
                    'company': q.get('company'),
                    'date': date_obj,
                    'category_id': category_id,
                    'topic_name': q.get('topic'),
                    'canonical_question': q.get('canonical_question')
                })
                question_counter += 1
            
            session.commit()
            print(f"Imported batch {i//batch_size + 1}")
        
        # Проверка
        cat_count = session.execute(text('SELECT COUNT(*) FROM "InterviewCategory"')).scalar()
        q_count = session.execute(text('SELECT COUNT(*) FROM "InterviewQuestion"')).scalar()
        
        print(f"Final counts: {cat_count} categories, {q_count} questions")
        print("Import completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()