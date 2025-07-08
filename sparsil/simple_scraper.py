#!/usr/bin/env python3
"""
Упрощенный скрипт для сбора истории чата через MCP Telegram
"""

import json
import re
import time
from datetime import datetime
from typing import List, Dict, Optional

class SimpleTelegramScraper:
    def __init__(self):
        self.chat_name = "chn[2071074234:9204039393350586818]"
        self.all_messages = []
        self.interview_keywords = [
            "собеседование", "интервью", "interview", "запись", "видео", 
            "аудио", "разбор", "ревью", "code review", "техническое",
            "задача", "алгоритм", "live coding", "скрин", "демо", "тест"
        ]
    
    def is_interview_related(self, text: str) -> bool:
        """Проверяет, связано ли сообщение с собеседованиями"""
        text_lower = text.lower()
        
        # Проверка по ключевым словам
        for keyword in self.interview_keywords:
            if keyword in text_lower:
                return True
                
        # Проверка на ссылки на видео/аудио
        if re.search(r'(https?://.*\.(mp4|mp3|avi|mov|webm|m4a|wav))', text):
            return True
            
        # Проверка на ссылки на популярные видео платформы
        if re.search(r'(youtube\.com|youtu\.be|vimeo\.com|telemost\.yandex\.ru)', text):
            return True
            
        # Проверка на код (многострочный текст с отступами)
        if len(text.split('\n')) > 3 and any(kw in text for kw in ['function', 'const', 'let', 'var', 'class', 'def', 'import']):
            return True
            
        return False
    
    def extract_code_blocks(self, text: str) -> List[str]:
        """Извлекает блоки кода из текста"""
        code_blocks = []
        
        # Ищем блоки кода в тройных кавычках
        code_pattern = r'```[\s\S]*?```'
        matches = re.findall(code_pattern, text)
        code_blocks.extend(matches)
        
        # Ищем блоки кода с отступами (простая эвристика)
        lines = text.split('\n')
        current_block = []
        
        for line in lines:
            if line.strip() and (line.startswith('    ') or line.startswith('\t')):
                current_block.append(line)
            else:
                if current_block and len(current_block) > 2:
                    code_blocks.append('\n'.join(current_block))
                current_block = []
                
        if current_block and len(current_block) > 2:
            code_blocks.append('\n'.join(current_block))
            
        return code_blocks
    
    def structure_message(self, message: Dict) -> Dict:
        """Структурирует сообщение для удобного анализа"""
        text = message.get("text", "")
        
        structured = {
            "author": message.get("who", "Unknown"),
            "timestamp": message.get("when", ""),
            "raw_text": text,
            "is_interview_related": self.is_interview_related(text),
            "code_blocks": self.extract_code_blocks(text),
            "links": re.findall(r'https?://[^\s]+', text),
            "message_length": len(text),
            "has_code": bool(self.extract_code_blocks(text)),
            "keywords_found": [kw for kw in self.interview_keywords if kw in text.lower()]
        }
        
        return structured
    
    def analyze_messages(self, messages: List[Dict]) -> Dict:
        """Анализирует сообщения и возвращает структурированные данные"""
        structured_messages = [self.structure_message(msg) for msg in messages]
        interview_messages = [msg for msg in structured_messages if msg["is_interview_related"]]
        
        # Группируем по авторам
        by_author = {}
        for msg in interview_messages:
            author = msg["author"]
            if author not in by_author:
                by_author[author] = []
            by_author[author].append(msg)
        
        # Статистика
        stats = {
            "total_messages": len(messages),
            "interview_messages": len(interview_messages),
            "unique_authors": len(by_author),
            "messages_with_code": len([msg for msg in interview_messages if msg["has_code"]]),
            "messages_with_links": len([msg for msg in interview_messages if msg["links"]]),
            "collection_date": datetime.now().isoformat()
        }
        
        return {
            "statistics": stats,
            "interview_messages": interview_messages,
            "messages_by_author": by_author,
            "all_structured_messages": structured_messages
        }
    
    def save_results(self, data: Dict, filename: str = "telegram_analysis.json"):
        """Сохраняет результаты в файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Результаты сохранены в {filename}")
    
    def print_summary(self, data: Dict):
        """Выводит краткую сводку"""
        stats = data["statistics"]
        interview_messages = data["interview_messages"]
        
        print("\n" + "="*60)
        print("АНАЛИЗ ЧАТА Frontend – TO THE JOB")
        print("="*60)
        
        print(f"\nОбщая статистика:")
        print(f"  Всего сообщений: {stats['total_messages']}")
        print(f"  Сообщения о собеседованиях: {stats['interview_messages']}")
        print(f"  Уникальных авторов: {stats['unique_authors']}")
        print(f"  Сообщения с кодом: {stats['messages_with_code']}")
        print(f"  Сообщения со ссылками: {stats['messages_with_links']}")
        
        # Топ авторов
        authors = {}
        for msg in interview_messages:
            author = msg["author"]
            authors[author] = authors.get(author, 0) + 1
            
        if authors:
            print(f"\nТоп авторов по сообщениям о собеседованиях:")
            for author, count in sorted(authors.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {author}: {count} сообщений")
        
        # Популярные ключевые слова
        all_keywords = []
        for msg in interview_messages:
            all_keywords.extend(msg["keywords_found"])
            
        if all_keywords:
            keyword_counts = {}
            for kw in all_keywords:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
                
            print(f"\nПопулярные ключевые слова:")
            for kw, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {kw}: {count} раз")
        
        # Примеры сообщений с записями
        print(f"\nПримеры сообщений с записями собеседований:")
        for i, msg in enumerate(interview_messages[:5]):
            print(f"\n{i+1}. {msg['author']} ({msg['timestamp']}):")
            text = msg['raw_text'][:200] + "..." if len(msg['raw_text']) > 200 else msg['raw_text']
            print(f"   {text}")
            if msg['links']:
                print(f"   Ссылки: {', '.join(msg['links'])}")
            if msg['keywords_found']:
                print(f"   Ключевые слова: {', '.join(msg['keywords_found'])}")

# Функция для ручного анализа уже полученных данных
def analyze_current_data():
    """Анализирует текущие данные из чата"""
    scraper = SimpleTelegramScraper()
    
    # Здесь вы можете вставить данные, полученные вручную
    # Пример данных (замените на реальные):
    sample_messages = [
        {"who": "budkakdomaputnic", "when": "2025-07-08 21:19:16", "text": "https://telemost.yandex.ru/j/13592002799790"},
        {"who": "VP262626", "when": "2025-07-08 18:10:48", "text": "async function fetchRetryer(url, counter = 5) {\n    let lastError = null;\n\n    for (let i = 0; i < counter; i++) {\n        try {\n            const response = await fetch(url);\n\n            if (response.ok) {\n                return await response.json();\n            } else {\n                lastError = new Error(`HTTP error! Status: ${response.status}`);\n            }\n        } catch (error) {\n            lastError = error;\n        }\n\n        if (i < counter - 1) {\n            await new Promise(resolve => setTimeout(resolve, 1000));\n        }\n    }\n\n    throw lastError;\n}"},
        # Добавьте больше сообщений здесь...
    ]
    
    data = scraper.analyze_messages(sample_messages)
    scraper.save_results(data)
    scraper.print_summary(data)
    
    return data

if __name__ == "__main__":
    print("Simple Telegram Chat Analyzer")
    print("="*40)
    
    # Для начала анализируем уже имеющиеся данные
    analyze_current_data() 