#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Постобработка результатов BERTopic с помощью GPT
Минимальные изменения для максимального эффекта
"""

import pandas as pd
import json
import os
from typing import List, Dict
import time

# Настройки API
API_KEY = "sk-yseNQGJXYUnn4YjrnwNJnwW7bsnwFg8K"  # Твой ProxyAPI ключ
API_BASE_URL = "https://api.proxyapi.ru/openai/v1"  # Предполагаемый URL ProxyAPI

def call_gpt(prompt: str, model: str = "gpt-4.1-mini") -> str:
    """Вызов GPT через ProxyAPI"""
    import requests
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 100
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
        print(f"Ошибка вызова API: {e}")
        # Возвращаем простое название на основе ключевых слов
        return prompt.split(',')[0].strip() if ',' in prompt else "Тема"

def generate_topic_name(keywords: str, sample_questions: List[str], size: int) -> str:
    """Генерация человеческого названия темы"""
    prompt = f"""Ты эксперт по техническим интервью в IT. Дай точное название для темы из {size} вопросов.

КЛЮЧЕВЫЕ СЛОВА: {keywords}

ПРИМЕРЫ ВОПРОСОВ:
{chr(10).join(f'• {q}' for q in sample_questions[:3])}

ПРАВИЛА:
✓ 2-4 слова на русском
✓ Техническое название (например: "Event Loop", "React хуки", "TypeScript типы")
✓ Без лишних слов типа "и его аспекты", "вопросы", "интервью"
✓ БЕЗ кавычек

ТОЛЬКО название темы:"""
    
    return call_gpt(prompt).strip().strip('"')

def find_duplicate_clusters(clusters_df: pd.DataFrame) -> List[List[int]]:
    """Находим дублирующиеся кластеры через GPT"""
    # Берем топ-50 кластеров для анализа
    top_clusters = clusters_df.head(50)
    
    clusters_info = []
    for _, row in top_clusters.iterrows():
        clusters_info.append({
            "id": row['cluster_id'],
            "keywords": row['topics'],
            "size": row['size']
        })
    
    prompt = f"""Проанализируй эти темы интервью и найди дублирующиеся/похожие.

{json.dumps(clusters_info, ensure_ascii=False, indent=2)}

Найди группы тем, которые стоит объединить (например, разные аспекты TypeScript или event loop).
Верни JSON массив групп: [[id1, id2], [id3, id4, id5], ...]
Только явные дубли!

Ответь ТОЛЬКО валидным JSON."""
    
    response = call_gpt(prompt)
    try:
        return json.loads(response)
    except:
        return []

def postprocess_bertopic_results(
    input_dir: str = "outputs_bertopic",
    output_dir: str = "outputs_bertopic_enhanced"
):
    """Главная функция постобработки"""
    print("="*60)
    print("🚀 ПОСТОБРАБОТКА РЕЗУЛЬТАТОВ BERTOPIC")
    print("="*60)
    
    # 1. Загружаем результаты
    print("\n📂 Загрузка файлов...")
    clusters_df = pd.read_csv(f"{input_dir}/cluster_labels.csv")
    questions_df = pd.read_csv(f"{input_dir}/questions_with_clusters.csv")
    
    print(f"   ✓ Загружено {len(clusters_df)} кластеров")
    print(f"   ✓ Загружено {len(questions_df)} вопросов")
    
    # 2. Генерируем человеческие названия
    print("\n🤖 Генерация названий тем через GPT...")
    print("   (это займет 2-3 минуты)")
    
    enhanced_clusters = []
    
    for idx, row in clusters_df.iterrows():
        cluster_id = row['cluster_id']
        
        # Получаем примеры вопросов для этого кластера
        cluster_questions = questions_df[
            questions_df['cluster_id'] == cluster_id
        ]['question_text'].head(5).tolist()
        
        # Генерируем название
        try:
            human_name = generate_topic_name(
                row['topics'], 
                cluster_questions,
                row['size']
            )
            
            # Определяем категорию
            category = classify_topic_category(human_name, row['topics'])
            
            enhanced_clusters.append({
                'cluster_id': cluster_id,
                'human_name': human_name,
                'category': category,
                'keywords': row['topics'],
                'size': row['size'],
                'canonical_question': row['canonical_question']
            })
            
            if idx % 10 == 0:
                print(f"   Обработано {idx}/{len(clusters_df)} тем...")
                
        except Exception as e:
            print(f"   ⚠️ Ошибка для кластера {cluster_id}: {e}")
            enhanced_clusters.append({
                'cluster_id': cluster_id,
                'human_name': row['topics'].split(',')[0].strip(),
                'category': 'Другое',
                'keywords': row['topics'],
                'size': row['size'],
                'canonical_question': row['canonical_question']
            })
        
        # Пауза чтобы не перегружать API
        if idx % 5 == 0:
            time.sleep(1)
    
    # 3. Находим и помечаем дубли
    print("\n🔍 Поиск дублирующихся тем...")
    duplicates = find_duplicate_clusters(clusters_df)
    
    if duplicates:
        print(f"   ✓ Найдено {len(duplicates)} групп дублей")
        # Помечаем дубли
        for group in duplicates:
            main_id = group[0]
            for dup_id in group[1:]:
                for cluster in enhanced_clusters:
                    if cluster['cluster_id'] == dup_id:
                        cluster['duplicate_of'] = main_id
    
    # 4. Сохраняем результаты
    print("\n💾 Сохранение улучшенных результатов...")
    os.makedirs(output_dir, exist_ok=True)
    
    # Сохраняем улучшенные кластеры
    enhanced_df = pd.DataFrame(enhanced_clusters)
    enhanced_df.to_csv(f"{output_dir}/clusters_enhanced.csv", index=False, encoding='utf-8-sig')
    print(f"   ✓ {output_dir}/clusters_enhanced.csv")
    
    # Создаем сводку по категориям
    category_summary = enhanced_df.groupby('category').agg({
        'size': 'sum',
        'cluster_id': 'count'
    }).rename(columns={'cluster_id': 'clusters_count'}).sort_values('size', ascending=False)
    
    category_summary.to_csv(f"{output_dir}/category_summary.csv", encoding='utf-8-sig')
    print(f"   ✓ {output_dir}/category_summary.csv")
    
    # Топ темы с человеческими названиями
    top_topics = enhanced_df.nlargest(20, 'size')[['human_name', 'category', 'size', 'keywords']]
    top_topics.to_csv(f"{output_dir}/top_topics_human.csv", index=False, encoding='utf-8-sig')
    print(f"   ✓ {output_dir}/top_topics_human.csv")
    
    print("\n" + "="*60)
    print("✅ ПОСТОБРАБОТКА ЗАВЕРШЕНА!")
    print(f"📁 Результаты в папке: {output_dir}/")
    print("="*60)
    
    return enhanced_df

def classify_topic_category(name: str, keywords: str) -> str:
    """Улучшенная классификация по категориям"""
    name_lower = name.lower()
    keywords_lower = keywords.lower()
    
    # Точные совпадения (приоритет)
    exact_matches = {
        'event loop': 'JavaScript Core',
        'event-loop': 'JavaScript Core', 
        'промис': 'JavaScript Core',
        'асинхрон': 'JavaScript Core',
        'замыкан': 'JavaScript Core',
        'прототип': 'JavaScript Core',
        'хук': 'React',
        'redux': 'React',
        'react': 'React',
        'состоян': 'React',
        'компонент': 'React',
        'типы': 'TypeScript',
        'typescript': 'TypeScript',
        'interface': 'TypeScript',
        'дженер': 'TypeScript',
        'css': 'Верстка',
        'html': 'Верстка',
        'flex': 'Верстка',
        'grid': 'Верстка',
        'алгоритм': 'Алгоритмы',
        'сложность': 'Алгоритмы',
        'массив': 'Алгоритмы',
        'числ': 'Алгоритмы',
        'http': 'Сеть',
        'cors': 'Сеть',
        'api': 'Сеть',
        'websocket': 'Сеть',
        'тест': 'Тестирование',
        'unit': 'Тестирование',
        'команд': 'Soft Skills',
        'опыт': 'Soft Skills',
        'проект': 'Soft Skills',
        'работ': 'Soft Skills',
        'развитие': 'Soft Skills',
        'git': 'Инструменты',
        'webpack': 'Инструменты',
        'npm': 'Инструменты',
        'node': 'Node.js',
        'express': 'Node.js',
        'backend': 'Node.js',
        'паттерн': 'Архитектура',
        'solid': 'Архитектура',
        'архитект': 'Архитектура',
    }
    
    # Ищем точные совпадения
    for pattern, category in exact_matches.items():
        if pattern in name_lower or pattern in keywords_lower:
            return category
    
    return 'Другое'

if __name__ == "__main__":
    postprocess_bertopic_results()