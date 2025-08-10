#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СОЗДАНИЕ ИТОГОВОГО ФАЙЛА СО ВСЕМИ ВОПРОСАМИ И ИХ КАТЕГОРИЯМИ
"""

import pandas as pd
import os

def main():
    print("СОЗДАНИЕ ИТОГОВОГО ФАЙЛА ВОПРОСОВ")
    print("=" * 50)
    
    # Загружаем исходные вопросы (полный набор данных)
    questions_df = pd.read_csv("outputs_bertopic/enriched_questions.csv")
    print(f"Загружено вопросов: {len(questions_df)}")
    
    # Загружаем финальные кластеры с категориями
    clusters_df = pd.read_csv("outputs_bertopic_final/clusters_final.csv")
    print(f"Загружено кластеров: {len(clusters_df)}")
    
    # Объединяем данные
    final_questions = questions_df.merge(
        clusters_df[['cluster_id', 'human_name', 'category']], 
        on='cluster_id', 
        how='left'
    )
    
    # Заполняем пропущенные значения
    final_questions['category'] = final_questions['category'].fillna('Нет кластера')
    final_questions['human_name'] = final_questions['human_name'].fillna('Нет темы')
    
    # Переименовываем колонки для удобства
    final_questions = final_questions.rename(columns={
        'human_name': 'topic_name',
        'category': 'final_category'
    })
    
    # Выбираем нужные колонки
    result_columns = [
        'id', 'question_text', 'company', 'date', 
        'cluster_id', 'topic_name', 'final_category',
        'canonical_question'
    ]
    
    final_result = final_questions[result_columns].copy()
    
    # Статистика
    print(f"\nСТАТИСТИКА:")
    print(f"Всего вопросов в итоговом файле: {len(final_result)}")
    print(f"Уникальных категорий: {final_result['final_category'].nunique()}")
    print(f"Вопросов без кластера: {len(final_result[final_result['final_category'] == 'Нет кластера'])}")
    
    # Распределение по категориям
    print(f"\nРАСПРЕДЕЛЕНИЕ ПО КАТЕГОРИЯМ:")
    category_stats = final_result['final_category'].value_counts()
    for category, count in category_stats.head(15).items():
        percentage = count / len(final_result) * 100
        print(f"   {category}: {count} ({percentage:.1f}%)")
    
    # Сохраняем результат
    output_dir = "outputs_bertopic_final"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f"{output_dir}/all_questions_with_categories.csv"
    final_result.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\nФАЙЛ СОХРАНЕН: {output_file}")
    print(f"Размер файла: {len(final_result)} строк x {len(final_result.columns)} колонок")
    
    # Также создаем упрощенную версию только с вопросами и категориями
    simple_version = final_result[['question_text', 'final_category', 'topic_name']].copy()
    simple_file = f"{output_dir}/questions_categories_simple.csv"
    simple_version.to_csv(simple_file, index=False, encoding='utf-8-sig')
    
    print(f"Упрощенная версия: {simple_file}")
    print("\nГОТОВО! Теперь у тебя есть полный список всех вопросов с категориями.")

if __name__ == "__main__":
    main()