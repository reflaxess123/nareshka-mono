#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль разделения составных вопросов на атомарные
Превращает одну строку с несколькими вопросами в отдельные записи
"""

import csv
import json
import logging
import requests
import re
from typing import List, Dict, Optional
import tiktoken

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionSplitter:
    """Разделяет составные вопросы на атомарные через GPT-4.1-mini"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.proxyapi.ru/openai/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        self.total_cost = 0
    
    def create_split_prompt(self, batch: List[Dict]) -> str:
        """Создание промпта для разделения"""
        prompt = """Разбей составные вопросы собеседований на смысловые АТОМАРНЫЕ блоки.

ПРИНЦИП РАЗДЕЛЕНИЯ:
- Разделяй только если это действительно РАЗНЫЕ независимые вопросы/задачи
- НЕ разделяй вопросы, которые связаны по смыслу и контексту
- Один концепт = один вопрос (даже если в нем несколько подпунктов)

ПРИМЕРЫ:
✅ РАЗДЕЛЯЙ: "1. Напиши функцию сортировки 2. Что такое замыкания" (разные темы)
❌ НЕ РАЗДЕЛЯЙ: "Что такое debounce? Для чего используется? Реализуй его" (один концепт)
❌ НЕ РАЗДЕЛЯЙ: "Объясни Promise и напиши пример" (одна тема)

ПРАВИЛА:
- Сохраняй оригинальную формулировку  
- Убирай только нумерацию (1., 2., ---)
- Объединяй связанные подвопросы в один блок

ФОРМАТ JSON:
[
  {
    "original_id": "исходный_id",
    "questions": [
      "первый смысловой блок",
      "второй смысловой блок"  
    ]
  }
]

ЗАПИСИ ДЛЯ РАЗДЕЛЕНИЯ:
"""
        
        for i, row in enumerate(batch):
            prompt += f"\n{i+1}. ID: {row['interview_id']}\n"
            prompt += f"   Текст: {row['text']}\n"
            
        return prompt
    
    def call_gpt(self, prompt: str) -> Optional[str]:
        """Вызов GPT-4.1-mini"""
        try:
            payload = {
                "model": "gpt-4.1-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "Разделяешь только действительно РАЗНЫЕ вопросы. НЕ разделяй смысловые блоки одной темы. Один концепт = один вопрос. JSON только."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 8000
            }
            
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=45
            )
            
            if response.status_code != 200:
                logger.error(f"API ошибка: {response.status_code}")
                return None
                
            # Подсчет стоимости
            usage = response.json().get('usage', {})
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)
            cost = (input_tokens * 0.15 / 1000000) + (output_tokens * 0.60 / 1000000)
            self.total_cost += cost
            
            logger.info(f"GPT-4.1-mini: {input_tokens} + {output_tokens} токенов, ${cost:.4f}")
            
            return response.json()['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"Ошибка API: {e}")
            return None
    
    def parse_split_response(self, response: str) -> List[Dict]:
        """Парсинг ответа GPT"""
        try:
            # Поиск JSON в ответе
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return []
        except Exception as e:
            logger.error(f"Ошибка парсинга: {e}")
            logger.error(f"Ответ: {response[:200]}...")
            return []
    
    def generate_atomic_id(self, original_id: str, question_index: int) -> str:
        """Генерация ID для атомарного вопроса"""
        if question_index == 0:
            return original_id  # Первый вопрос сохраняет оригинальный ID
        else:
            return f"{original_id}_q{question_index + 1}"
    
    def split_batch(self, batch: List[Dict]) -> List[Dict]:
        """Разделение батча записей"""
        logger.info(f"Разделяем батч из {len(batch)} записей...")
        
        prompt = self.create_split_prompt(batch)
        response = self.call_gpt(prompt)
        
        if not response:
            logger.error("Не удалось получить ответ от API")
            return batch  # Возвращаем оригинал
            
        split_results = self.parse_split_response(response)
        
        if not split_results:
            logger.error("Не удалось парсить ответ")
            return batch
            
        # Создаем атомарные записи
        atomic_rows = []
        split_dict = {item['original_id']: item['questions'] for item in split_results}
        
        for row in batch:
            original_id = row['interview_id']
            questions = split_dict.get(original_id, [row['text']])  # fallback к оригиналу
            
            # Создаем отдельную запись для каждого вопроса
            for i, question in enumerate(questions):
                atomic_row = row.copy()
                atomic_row['interview_id'] = self.generate_atomic_id(original_id, i)
                atomic_row['text'] = question.strip()
                atomic_row['parent_interview_id'] = original_id  # Связь с оригиналом
                atomic_row['question_index'] = str(i + 1)  # Номер подвопроса
                atomic_rows.append(atomic_row)
        
        logger.info(f"Из {len(batch)} записей получили {len(atomic_rows)} атомарных")
        return atomic_rows
    
    def split_csv(self, input_path: str, output_path: str, batch_size: int = 3):
        """Разделение всего CSV файла"""
        logger.info(f"Начинаем разделение {input_path}")
        
        # Читаем исходный файл
        rows = []
        with open(input_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        logger.info(f"Загружено {len(rows)} составных записей")
        
        # Разделяем батчами
        all_atomic_rows = []
        
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            logger.info(f"Обрабатываем батч {i//batch_size + 1}/{(len(rows) + batch_size - 1)//batch_size}")
            
            atomic_batch = self.split_batch(batch)
            all_atomic_rows.extend(atomic_batch)
        
        # Добавляем новые поля в заголовок
        if all_atomic_rows:
            # Определяем все возможные поля
            all_fields = set()
            for row in all_atomic_rows:
                all_fields.update(row.keys())
            
            fieldnames = list(all_fields)
            
            # Сохраняем результат с правильным экранированием
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(
                    f, 
                    fieldnames=fieldnames, 
                    quoting=csv.QUOTE_ALL,
                    quotechar='"',
                    escapechar='\\',
                    doublequote=True
                )
                writer.writeheader()
                writer.writerows(all_atomic_rows)
                
        logger.info(f"Разделение завершено!")
        logger.info(f"Из {len(rows)} составных записей получили {len(all_atomic_rows)} атомарных")
        logger.info(f"Общая стоимость: ${self.total_cost:.4f}")
        logger.info(f"Сохранено в {output_path}")


def main():
    """Запуск разделения"""
    API_KEY = "sk-yseNQGJXYUnn4YjrnwNJnwW7bsnwFg8K"
    INPUT_FILE = "interview_questions_cleaned.csv"
    OUTPUT_FILE = "interview_questions_atomic.csv"
    
    splitter = QuestionSplitter(API_KEY)
    splitter.split_csv(INPUT_FILE, OUTPUT_FILE, batch_size=3)


if __name__ == "__main__":
    main()