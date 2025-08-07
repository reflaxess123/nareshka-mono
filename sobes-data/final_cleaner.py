#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная очистка CSV - оставляем только полезные поля
Убираем пустые и бесполезные столбцы
"""

import csv
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_final_csv(input_path: str, output_path: str):
    """Очищает CSV, оставляя только полезные поля"""
    
    # Полезные поля для ML-анализа
    useful_fields = [
        'interview_id',           # Уникальный ID
        'parent_interview_id',    # Связь с оригиналом
        'question_index',         # Номер подвопроса
        'company',               # Компания (ключевое поле)
        'type',                  # Тип вопроса
        'text',                  # Основной контент
        'date',                  # Временная метка
        'time',                  # Время
        'source'                 # Источник данных
    ]
    
    logger.info(f"Читаем {input_path}")
    
    # Читаем исходный файл
    rows = []
    with open(input_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        original_fields = reader.fieldnames
        
        for row in reader:
            # Извлекаем только полезные поля
            clean_row = {}
            for field in useful_fields:
                clean_row[field] = row.get(field, '')
            rows.append(clean_row)
    
    logger.info(f"Загружено {len(rows)} записей")
    logger.info(f"Удалены поля: {set(original_fields) - set(useful_fields)}")
    
    # Сохраняем очищенный файл
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(
            f, 
            fieldnames=useful_fields,
            quoting=csv.QUOTE_ALL
        )
        writer.writeheader()
        writer.writerows(rows)
    
    logger.info(f"Финальная база сохранена в {output_path}")
    logger.info(f"Поля: {', '.join(useful_fields)}")
    
    # Статистика
    print(f"\nФИНАЛЬНАЯ БАЗА ГОТОВА!")
    print(f"Записей: {len(rows)}")
    print(f"Полей: {len(useful_fields)}")
    print(f"Файл: {output_path}")
    
    # Краткая аналитика
    companies = {}
    types = {}
    
    for row in rows:
        company = row['company']
        row_type = row['type']
        
        companies[company] = companies.get(company, 0) + 1
        types[row_type] = types.get(row_type, 0) + 1
    
    print(f"\nКомпании:")
    for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True):
        print(f"  {company}: {count}")
        
    print(f"\nТипы вопросов:")
    for q_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {q_type}: {count}")


def main():
    """Запуск финальной очистки"""
    INPUT_FILE = "interview_questions_atomic.csv"
    OUTPUT_FILE = "interview_questions_final.csv"
    
    clean_final_csv(INPUT_FILE, OUTPUT_FILE)


if __name__ == "__main__":
    main()