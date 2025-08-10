#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
УЛУЧШЕННАЯ GPT ПОСТОБРАБОТКА V2
- GPT-4.1-mini вместо 4o-mini
- Лучшие промпты
- Улучшенная категоризация
- Исправление существующих результатов
"""

import pandas as pd
import os
import time
import requests
from typing import List, Dict

# Настройки API
API_KEY = "sk-yseNQGJXYUnn4YjrnwNJnwW7bsnwFg8K"
API_BASE_URL = "https://api.proxyapi.ru/openai/v1"

def call_gpt(prompt: str, model: str = "gpt-4.1-mini") -> str:
    """Вызов GPT через ProxyAPI"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,  # Более детерминированно
        "max_tokens": 50      # Короткие названия
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Ошибка API: {e}")
        return "Тема"

def improve_topic_name(old_name: str, keywords: str, sample_questions: List[str]) -> str:
    """Улучшение существующего названия темы"""
    prompt = f"""Ты эксперт по техническим интервью. Улучши название темы для IT собеседований.

ТЕКУЩЕЕ НАЗВАНИЕ: "{old_name}"
КЛЮЧЕВЫЕ СЛОВА: {keywords}
ПРИМЕРЫ ВОПРОСОВ:
• {sample_questions[0] if sample_questions else 'Нет примеров'}

ТРЕБОВАНИЯ:
✓ 1-3 слова максимум
✓ Техничное и точное (Event Loop, React Hooks, CSS Grid)
✓ На русском, но можно оставить англицизмы если они устоявшиеся
✓ Убери лишние слова "аспекты", "вопросы", "технологии"

УЛУЧШЕННОЕ НАЗВАНИЕ:"""
    
    improved = call_gpt(prompt).strip().strip('"').strip("'")
    return improved if improved != "Тема" else old_name

def fix_wrong_categories():
    """Исправляет неправильные категории из первого прогона"""
    fixes = {
        "Поиск нового места работы": "Soft Skills",
        "Числовые задачи массива": "Алгоритмы", 
        "Циклы событий в микрообработке": "JavaScript Core",
        "Современные веб-технологии": "JavaScript Core",
        "Код-ревью и внимание": "Soft Skills",
        "Функциональное программирование": "JavaScript Core",
        "Браузерные хранилища": "JavaScript Core",
    }
    return fixes

def main():
    print("🔧 УЛУЧШЕННАЯ ПОСТОБРАБОТКА V2")
    print("=" * 50)
    
    # 1. Загружаем существующие результаты
    input_file = "outputs_bertopic_enhanced/clusters_enhanced.csv"
    if not os.path.exists(input_file):
        print("❌ Сначала запусти базовую постобработку!")
        return
    
    df = pd.read_csv(input_file)
    print(f"📂 Загружено {len(df)} кластеров")
    
    # 2. Исправляем категории
    print("\n🏷️  Исправление категорий...")
    category_fixes = fix_wrong_categories()
    
    for idx, row in df.iterrows():
        name = row['human_name']
        keywords = row['keywords']
        
        # Исправляем известные ошибки категоризации
        if name in category_fixes:
            df.at[idx, 'category'] = category_fixes[name]
            print(f"   ✓ {name} → {category_fixes[name]}")
        
        # Улучшенная автокатегоризация для остальных
        elif row['category'] == 'Другое':
            new_category = smart_categorize(name, keywords)
            if new_category != 'Другое':
                df.at[idx, 'category'] = new_category
                print(f"   ✓ {name} → {new_category}")
    
    # 3. Улучшаем названия проблемных тем
    print("\n📝 Улучшение названий...")
    problem_names = [
        "Хуки и факапы", 
        "Циклы событий в микрообработке",
        "Современные веб-технологии",
        "Поиск нового места работы"
    ]
    
    # Загружаем вопросы один раз
    questions_df = pd.read_csv("outputs_bertopic/questions_with_clusters.csv")
    
    for idx, row in df.iterrows():
        if row['human_name'] in problem_names:
            # Получаем примеры вопросов для этого кластера
            cluster_questions = questions_df[
                questions_df['cluster_id'] == row['cluster_id']
            ]['question_text'].head(3).tolist()
            
            improved_name = improve_topic_name(
                row['human_name'], 
                row['keywords'], 
                cluster_questions
            )
            
            if improved_name != row['human_name']:
                df.at[idx, 'human_name'] = improved_name
                print(f"   ✓ {row['human_name']} → {improved_name}")
                time.sleep(1)  # Пауза между API вызовами
    
    # 4. Сохраняем улучшенные результаты
    output_dir = "outputs_bertopic_v2"
    os.makedirs(output_dir, exist_ok=True)
    
    # Основной файл
    df.to_csv(f"{output_dir}/clusters_enhanced_v2.csv", index=False, encoding='utf-8-sig')
    print(f"\n💾 Сохранено: {output_dir}/clusters_enhanced_v2.csv")
    
    # Обновленная сводка по категориям
    category_summary = df.groupby('category').agg({
        'size': 'sum',
        'cluster_id': 'count'
    }).rename(columns={'cluster_id': 'clusters_count'}).sort_values('size', ascending=False)
    
    category_summary.to_csv(f"{output_dir}/category_summary_v2.csv", encoding='utf-8-sig')
    print(f"💾 Сохранено: {output_dir}/category_summary_v2.csv")
    
    # Топ темы
    top_topics = df.nlargest(20, 'size')[['human_name', 'category', 'size', 'keywords']]
    top_topics.to_csv(f"{output_dir}/top_topics_v2.csv", index=False, encoding='utf-8-sig')
    print(f"💾 Сохранено: {output_dir}/top_topics_v2.csv")
    
    print("\n" + "✅" * 30)
    print("УЛУЧШЕНИЕ ЗАВЕРШЕНО!")
    print(f"Результаты в папке: {output_dir}/")
    print("✅" * 30)

def smart_categorize(name: str, keywords: str) -> str:
    """Умная категоризация на основе контекста"""
    name_lower = name.lower()
    keywords_lower = keywords.lower()
    
    patterns = {
        'JavaScript Core': ['event', 'loop', 'промис', 'асинхрон', 'замыкан', 'this', 'prototype'],
        'React': ['хук', 'hook', 'react', 'компонент', 'jsx', 'props', 'state', 'redux'],
        'TypeScript': ['typescript', 'тип', 'type', 'interface', 'generic'],
        'Верстка': ['css', 'html', 'flex', 'grid', 'layout', 'анимац'],
        'Алгоритмы': ['алгоритм', 'сложность', 'массив', 'числ', 'сортир', 'поиск'],
        'Soft Skills': ['опыт', 'команд', 'проект', 'работ', 'развитие', 'карьер'],
        'Сеть': ['http', 'api', 'cors', 'rest', 'websocket', 'запрос'],
        'Тестирование': ['тест', 'unit', 'jest', 'mock'],
    }
    
    for category, words in patterns.items():
        if any(word in name_lower or word in keywords_lower for word in words):
            return category
    
    return 'Другое'

if __name__ == "__main__":
    main()