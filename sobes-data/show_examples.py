#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def show_truncation_examples():
    file_path = r"C:\Users\refla\nareshka-mono\sobes-data\MASSIV_GROUPED.json"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("ПРИМЕРЫ ОБРЕЗАННОГО КОНТЕНТА:")
    print("="*60)
    
    count = 0
    for company_data in data:
        if 'records' in company_data and count < 3:
            for record in company_data['records']:
                if count < 3:
                    content = record.get('content', '')
                    full_content = record.get('full_content', '')
                    
                    if content.rstrip().endswith('...') and len(full_content) > len(content):
                        count += 1
                        print(f"\nПРИМЕР {count}:")
                        print(f"Компания: {company_data.get('company', 'Unknown')}")
                        print(f"Дата: {record.get('timestamp', 'Unknown')}")
                        print(f"Длина content: {len(content)} символов")
                        print(f"Длина full_content: {len(full_content)} символов")
                        print(f"Разница: {len(full_content) - len(content)} символов")
                        print()
                        print("CONTENT (обрезан):")
                        print(f"Начало: {content[:100]}...")
                        print(f"Конец: ...{content[-100:]}")
                        print()
                        print("FULL_CONTENT (полный):")
                        print(f"Начало: {full_content[:100]}...")
                        print(f"Конец: ...{full_content[-100:]}")
                        print("-" * 60)
                    
if __name__ == "__main__":
    show_truncation_examples()