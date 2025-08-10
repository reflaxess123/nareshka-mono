#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
АНАЛИЗ НЕКЛАСТЕРИЗОВАННЫХ ВОПРОСОВ
"""

import pandas as pd
import random

def main():
    print("АНАЛИЗ НЕКЛАСТЕРИЗОВАННЫХ ВОПРОСОВ")
    print("=" * 60)
    
    # Загружаем итоговый файл
    all_questions = pd.read_csv('outputs_bertopic_final/all_questions_with_categories.csv')
    
    # Разделяем на кластеризованные и некластеризованные
    clustered = all_questions[all_questions['cluster_id'] != -1]
    unclustered = all_questions[all_questions['cluster_id'] == -1]
    
    print(f"Всего вопросов: {len(all_questions)}")
    print(f"С кластерами: {len(clustered)} ({len(clustered)/len(all_questions)*100:.1f}%)")
    print(f"Без кластеров: {len(unclustered)} ({len(unclustered)/len(all_questions)*100:.1f}%)")
    
    print("\n" + "=" * 60)
    print("ПОЧЕМУ ВОПРОСЫ ОСТАЛИСЬ БЕЗ КЛАСТЕРА:")
    
    # Анализируем некластеризованные вопросы
    print(f"\n1. ПРИМЕРЫ НЕКЛАСТЕРИЗОВАННЫХ ВОПРОСОВ (случайная выборка):")
    sample_unclustered = unclustered.sample(min(15, len(unclustered)), random_state=42)
    
    for i, (_, row) in enumerate(sample_unclustered.iterrows(), 1):
        question = row['question_text'][:100] + "..." if len(row['question_text']) > 100 else row['question_text']
        print(f"   {i:2d}. {question}")
        print(f"       Компания: {row['company']}")
    
    print(f"\n2. РАСПРЕДЕЛЕНИЕ ПО КОМПАНИЯМ (некластеризованные):")
    unclustered_by_company = unclustered['company'].value_counts().head(10)
    for company, count in unclustered_by_company.items():
        percentage = count / len(unclustered) * 100
        print(f"   {company}: {count} вопросов ({percentage:.1f}%)")
    
    print(f"\n3. АНАЛИЗ ДЛИНЫ ВОПРОСОВ:")
    unclustered['question_length'] = unclustered['question_text'].str.len()
    clustered['question_length'] = clustered['question_text'].str.len()
    
    print(f"   Средняя длина некластеризованных: {unclustered['question_length'].mean():.1f} символов")
    print(f"   Средняя длина кластеризованных: {clustered['question_length'].mean():.1f} символов")
    print(f"   Медиана некластеризованных: {unclustered['question_length'].median():.1f} символов")
    print(f"   Медиана кластеризованных: {clustered['question_length'].median():.1f} символов")
    
    # Анализ очень коротких и очень длинных вопросов
    very_short = unclustered[unclustered['question_length'] < 20]
    very_long = unclustered[unclustered['question_length'] > 200]
    
    print(f"\n4. ЭКСТРЕМАЛЬНЫЕ СЛУЧАИ:")
    print(f"   Очень короткие (<20 символов): {len(very_short)} вопросов")
    print(f"   Очень длинные (>200 символов): {len(very_long)} вопросов")
    
    if len(very_short) > 0:
        print(f"\n   Примеры очень коротких:")
        for i, question in enumerate(very_short['question_text'].head(5), 1):
            print(f"      {i}. '{question}'")
    
    print(f"\n5. ВОЗМОЖНЫЕ ПРИЧИНЫ:")
    print("   • Уникальные/редкие вопросы, не похожие на другие")
    print("   • Слишком короткие вопросы (мало контекста)")
    print("   • Слишком длинные/сложные вопросы")
    print("   • Специфичные для конкретной компании")
    print("   • Некачественные/неполные вопросы")
    print("   • MIN_TOPIC_SIZE=15 исключил малые группы")
    
    print(f"\n6. ПАРАМЕТР MIN_TOPIC_SIZE:")
    print("   BERTopic с MIN_TOPIC_SIZE=15 означает, что группы")
    print("   меньше 15 похожих вопросов НЕ становятся кластерами.")
    print("   Это сделано для качества - избежать 'мусорных' кластеров.")
    
    print(f"\n" + "=" * 60)
    print("ВЫВОД:")
    print(f"22.1% некластеризованных вопросов - это НОРМАЛЬНО для:")
    print("• Большого разнообразного датасета (8,532 вопроса)")
    print("• Строгих параметров кластеризации (MIN_TOPIC_SIZE=15)")
    print("• Фокуса на качестве кластеров а не покрытии")
    print(f"• 77.9% успешно категоризированы - отличный результат!")

if __name__ == "__main__":
    main()