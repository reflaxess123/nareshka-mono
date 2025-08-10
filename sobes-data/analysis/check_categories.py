#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПРОВЕРКА ПРАВИЛЬНОСТИ РАСПРЕДЕЛЕНИЯ КАТЕГОРИЙ
"""

import pandas as pd

def main():
    # Загружаем наши доработанные кластеры
    clusters_final = pd.read_csv('outputs_bertopic_final/clusters_final.csv')
    print('НАШИ ДОРАБОТАННЫЕ КЛАСТЕРЫ:')
    print(f'Всего кластеров: {len(clusters_final)}')
    print('Распределение по категориям в кластерах:')
    cluster_cats = clusters_final['category'].value_counts()
    for cat, count in cluster_cats.items():
        total_questions = clusters_final[clusters_final['category'] == cat]['size'].sum()
        print(f'  {cat}: {count} кластеров, {total_questions} вопросов')

    print('\n' + '='*60)

    # Загружаем итоговый файл вопросов  
    all_questions = pd.read_csv('outputs_bertopic_final/all_questions_with_categories.csv')
    print('ИТОГОВЫЙ ФАЙЛ ВОПРОСОВ:')
    print(f'Всего вопросов: {len(all_questions)}')

    # Только вопросы с кластерами (не -1)
    clustered = all_questions[all_questions['cluster_id'] != -1]
    print(f'Вопросов с кластерами: {len(clustered)}')

    print('Распределение по категориям в вопросах:')
    question_cats = clustered['final_category'].value_counts()
    for cat, count in question_cats.items():
        print(f'  {cat}: {count} вопросов')

    print('\n' + '='*60)
    print('СРАВНЕНИЕ:')
    print('Совпадают ли числа вопросов?')
    
    all_match = True
    for cat in cluster_cats.index:
        cluster_total = clusters_final[clusters_final['category'] == cat]['size'].sum()
        question_total = len(clustered[clustered['final_category'] == cat])
        match = cluster_total == question_total
        match_str = 'OK' if match else 'ERROR!'
        print(f'  {cat}: кластеры={cluster_total}, вопросы={question_total} {match_str}')
        if not match:
            all_match = False
    
    print('\n' + '='*60)
    if all_match:
        print('ВСЕ ПРАВИЛЬНО! Категории распределены корректно.')
        print('Наши доработанные кластеры точно соответствуют итоговому файлу вопросов.')
    else:
        print('ЕСТЬ НЕСООТВЕТСТВИЯ! Нужно проверить.')

if __name__ == "__main__":
    main()