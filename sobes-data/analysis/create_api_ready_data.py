#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СОЗДАНИЕ ДАННЫХ ГОТОВЫХ ДЛЯ API И ИНТЕГРАЦИИ
"""

import pandas as pd
import json
import os
from typing import Dict, List, Any

def create_api_ready_data():
    print("СОЗДАНИЕ ДАННЫХ ДЛЯ ИНТЕГРАЦИИ В ПРИЛОЖЕНИЕ")
    print("=" * 60)
    
    # Загружаем все финальные данные
    all_questions = pd.read_csv('outputs_bertopic_final/all_questions_with_categories.csv')
    clusters = pd.read_csv('outputs_bertopic_final/clusters_final.csv')
    categories = pd.read_csv('outputs_bertopic_final/category_summary_final.csv')
    
    # Создаем директорию для API данных
    output_dir = 'outputs_api_ready'
    os.makedirs(output_dir, exist_ok=True)
    
    # ========== 1. ОСНОВНОЙ ФАЙЛ ДЛЯ BACKEND ==========
    print("\n1. СОЗДАНИЕ ОСНОВНОГО ФАЙЛА ДЛЯ BACKEND")
    
    # Готовим данные по вопросам
    questions_api = []
    for _, row in all_questions.iterrows():
        questions_api.append({
            'id': row['id'],
            'question': row['question_text'],
            'company': row['company'],
            'date': row['date'] if pd.notna(row['date']) else None,
            'cluster_id': int(row['cluster_id']) if row['cluster_id'] != -1 else None,
            'topic': row['topic_name'] if pd.notna(row['topic_name']) else None,
            'category': row['final_category'] if row['final_category'] != 'Нет кластера' else None,
            'canonical_question': row['canonical_question'] if pd.notna(row['canonical_question']) else None
        })
    
    # Сохраняем для backend
    with open(f'{output_dir}/questions_full.json', 'w', encoding='utf-8') as f:
        json.dump(questions_api, f, ensure_ascii=False, indent=2)
    
    print(f"   Создан: questions_full.json ({len(questions_api)} вопросов)")
    
    # ========== 2. ДАННЫЕ ПО КАТЕГОРИЯМ ==========
    print("\n2. СОЗДАНИЕ ДАННЫХ ПО КАТЕГОРИЯМ")
    
    categories_api = []
    for _, row in categories.iterrows():
        categories_api.append({
            'name': row['category'],
            'questions_count': int(row['size']),
            'clusters_count': int(row['clusters_count']),
            'percentage': round(row['size'] / all_questions.shape[0] * 100, 2)
        })
    
    with open(f'{output_dir}/categories.json', 'w', encoding='utf-8') as f:
        json.dump(categories_api, f, ensure_ascii=False, indent=2)
    
    print(f"   Создан: categories.json ({len(categories_api)} категорий)")
    
    # ========== 3. ДАННЫЕ ПО КЛАСТЕРАМ/ТОПИКАМ ==========
    print("\n3. СОЗДАНИЕ ДАННЫХ ПО КЛАСТЕРАМ")
    
    clusters_api = []
    for _, row in clusters.iterrows():
        clusters_api.append({
            'id': int(row['cluster_id']),
            'name': row['human_name'],
            'category': row['category'],
            'keywords': row['keywords'].split(', '),
            'questions_count': int(row['size']),
            'example_question': row['canonical_question']
        })
    
    with open(f'{output_dir}/clusters.json', 'w', encoding='utf-8') as f:
        json.dump(clusters_api, f, ensure_ascii=False, indent=2)
    
    print(f"   Создан: clusters.json ({len(clusters_api)} кластеров)")
    
    # ========== 4. СТРУКТУРА ДЛЯ FRONTEND НАВИГАЦИИ ==========
    print("\n4. СОЗДАНИЕ СТРУКТУРЫ ДЛЯ FRONTEND")
    
    # Группируем по категориям для удобной навигации
    frontend_structure = {}
    
    for category in categories['category'].unique():
        category_clusters = clusters[clusters['category'] == category]
        category_questions = all_questions[all_questions['final_category'] == category]
        
        frontend_structure[category] = {
            'name': category,
            'total_questions': len(category_questions),
            'total_clusters': len(category_clusters),
            'percentage': round(len(category_questions) / len(all_questions) * 100, 2),
            'topics': []
        }
        
        for _, cluster in category_clusters.iterrows():
            cluster_questions = all_questions[all_questions['cluster_id'] == cluster['cluster_id']]
            
            frontend_structure[category]['topics'].append({
                'id': int(cluster['cluster_id']),
                'name': cluster['human_name'],
                'keywords': cluster['keywords'].split(', ')[:5],  # топ-5 ключевых слов
                'questions_count': len(cluster_questions),
                'example_questions': cluster_questions['question_text'].head(3).tolist()
            })
        
        # Сортируем топики по популярности
        frontend_structure[category]['topics'].sort(key=lambda x: x['questions_count'], reverse=True)
    
    with open(f'{output_dir}/frontend_structure.json', 'w', encoding='utf-8') as f:
        json.dump(frontend_structure, f, ensure_ascii=False, indent=2)
    
    print(f"   Создан: frontend_structure.json")
    
    # ========== 5. СТАТИСТИКА ДЛЯ DASHBOARD ==========
    print("\n5. СОЗДАНИЕ СТАТИСТИКИ ДЛЯ DASHBOARD")
    
    # Считаем статистику по компаниям
    company_stats = all_questions['company'].value_counts().head(20).to_dict()
    
    dashboard_stats = {
        'total_questions': len(all_questions),
        'categorized_questions': len(all_questions[all_questions['cluster_id'] != -1]),
        'total_categories': len(categories),
        'total_clusters': len(clusters),
        'total_companies': all_questions['company'].nunique(),
        'categorization_rate': round(len(all_questions[all_questions['cluster_id'] != -1]) / len(all_questions) * 100, 2),
        'top_companies': [
            {'name': company, 'count': int(count)} 
            for company, count in company_stats.items()
        ],
        'category_distribution': categories_api,
        'top_topics': clusters.nlargest(10, 'size')[['human_name', 'category', 'size']].to_dict('records')
    }
    
    with open(f'{output_dir}/dashboard_stats.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_stats, f, ensure_ascii=False, indent=2)
    
    print(f"   Создан: dashboard_stats.json")
    
    # ========== 6. ЛЕГКОВЕСНАЯ ВЕРСИЯ ДЛЯ ПОИСКА ==========
    print("\n6. СОЗДАНИЕ ДАННЫХ ДЛЯ ПОИСКА")
    
    search_data = []
    for _, row in all_questions.iterrows():
        if row['cluster_id'] != -1:  # только категоризованные
            search_data.append({
                'id': row['id'],
                'q': row['question_text'][:200],  # сокращаем для экономии места
                'c': row['final_category'],
                't': row['topic_name'],
                'co': row['company'][:50] if pd.notna(row['company']) else None
            })
    
    with open(f'{output_dir}/search_index.json', 'w', encoding='utf-8') as f:
        json.dump(search_data, f, ensure_ascii=False)
    
    print(f"   Создан: search_index.json ({len(search_data)} записей)")
    
    # ========== 7. CSV ВЕРСИИ ДЛЯ БАЗЫ ДАННЫХ ==========
    print("\n7. СОЗДАНИЕ CSV ДЛЯ ИМПОРТА В БД")
    
    # Упрощенная версия для БД
    db_export = all_questions[['id', 'question_text', 'company', 'cluster_id', 'final_category', 'topic_name']].copy()
    db_export.to_csv(f'{output_dir}/questions_for_db.csv', index=False, encoding='utf-8-sig')
    
    print(f"   Создан: questions_for_db.csv")
    
    print("\n" + "=" * 60)
    print("ГОТОВО! Все данные для интеграции созданы в папке outputs_api_ready/")
    print("\nФАЙЛЫ ДЛЯ BACKEND:")
    print("  • questions_full.json - все вопросы с категориями")
    print("  • categories.json - список категорий со статистикой")
    print("  • clusters.json - все кластеры/топики")
    print("  • questions_for_db.csv - для импорта в базу данных")
    print("\nФАЙЛЫ ДЛЯ FRONTEND:")
    print("  • frontend_structure.json - структурированные данные для UI")
    print("  • dashboard_stats.json - статистика для дашборда")
    print("  • search_index.json - легковесный индекс для поиска")
    
    return output_dir

if __name__ == "__main__":
    create_api_ready_data()