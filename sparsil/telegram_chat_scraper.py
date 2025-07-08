#!/usr/bin/env python3
"""
Скрипт для сбора всей истории чата Frontend – TO THE JOB с записями собеседований
"""

import json
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
import subprocess
import sys

class TelegramChatScraper:
    def __init__(self, chat_name: str = "chn[2071074234:9204039393350586818]"):
        self.chat_name = chat_name
        self.all_messages = []
        self.interview_keywords = [
            "собеседование", "интервью", "interview", "запись", "видео", 
            "аудио", "разбор", "ревью", "code review", "техническое",
            "задача", "алгоритм", "live coding", "скрин", "демо"
        ]
        
    def call_mcp_telegram(self, offset: Optional[int] = None) -> Dict:
        """Вызов MCP Telegram API для получения сообщений"""
        try:
            cmd = ["npx", "-y", "@chaindead/telegram-mcp"]
            
            # Формируем запрос
            request = {
                "method": "tg_dialog",
                "params": {
                    "name": self.chat_name
                }
            }
            
            if offset is not None:
                request["params"]["offset"] = offset
                
            # Выполняем запрос
            process = subprocess.run(
                cmd,
                input=json.dumps(request),
                text=True,
                capture_output=True,
                env={
                    "TG_APP_ID": "23628237",
                    "TG_API_HASH": "b4fed8cf04844f325c5fc228397852b5"
                }
            )
            
            if process.returncode != 0:
                print(f"Ошибка выполнения команды: {process.stderr}")
                return {}
                
            return json.loads(process.stdout)
            
        except Exception as e:
            print(f"Ошибка при вызове MCP API: {e}")
            return {}
    
    def collect_all_messages(self) -> List[Dict]:
        """Собирает все сообщения из чата"""
        print("Начинаю сбор всех сообщений из чата...")
        
        offset = None
        page = 1
        
        while True:
            print(f"Страница {page}, offset: {offset}")
            
            response = self.call_mcp_telegram(offset)
            
            if not response or "messages" not in response:
                print("Нет больше сообщений или ошибка API")
                break
                
            messages = response["messages"]
            
            if not messages:
                print("Достигнут конец истории чата")
                break
                
            self.all_messages.extend(messages)
            print(f"Получено {len(messages)} сообщений. Всего: {len(self.all_messages)}")
            
            # Получаем новый offset для следующей страницы
            if "offset" in response:
                offset = response["offset"]
            else:
                break
                
            page += 1
            time.sleep(1)  # Пауза между запросами
            
        print(f"Всего собрано {len(self.all_messages)} сообщений")
        return self.all_messages
    
    def is_interview_related(self, message: Dict) -> bool:
        """Проверяет, связано ли сообщение с собеседованиями"""
        text = message.get("text", "").lower()
        
        # Проверка по ключевым словам
        for keyword in self.interview_keywords:
            if keyword in text:
                return True
                
        # Проверка на ссылки на видео/аудио
        if re.search(r'(https?://.*\.(mp4|mp3|avi|mov|webm|m4a|wav))', text):
            return True
            
        # Проверка на ссылки на популярные видео платформы
        if re.search(r'(youtube\.com|youtu\.be|vimeo\.com|telemost\.yandex\.ru)', text):
            return True
            
        # Проверка на код (многострочный текст с отступами)
        if len(text.split('\n')) > 3 and any(keyword in text for keyword in ['function', 'const', 'let', 'var', 'class', 'def', 'import']):
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
            "is_interview_related": self.is_interview_related(message),
            "code_blocks": self.extract_code_blocks(text),
            "links": re.findall(r'https?://[^\s]+', text),
            "message_length": len(text),
            "has_code": bool(self.extract_code_blocks(text)),
            "keywords_found": [kw for kw in self.interview_keywords if kw in text.lower()]
        }
        
        return structured
    
    def filter_interview_messages(self, messages: List[Dict]) -> List[Dict]:
        """Фильтрует сообщения, связанные с собеседованиями"""
        structured_messages = [self.structure_message(msg) for msg in messages]
        interview_messages = [msg for msg in structured_messages if msg["is_interview_related"]]
        
        print(f"Найдено {len(interview_messages)} сообщений, связанных с собеседованиями")
        return interview_messages
    
    def save_results(self, messages: List[Dict], filename: str = "interview_records.json"):
        """Сохраняет результаты в файл"""
        # Группируем по авторам
        by_author = {}
        for msg in messages:
            author = msg["author"]
            if author not in by_author:
                by_author[author] = []
            by_author[author].append(msg)
        
        # Статистика
        stats = {
            "total_messages": len(messages),
            "unique_authors": len(by_author),
            "messages_with_code": len([msg for msg in messages if msg["has_code"]]),
            "messages_with_links": len([msg for msg in messages if msg["links"]]),
            "collection_date": datetime.now().isoformat()
        }
        
        result = {
            "statistics": stats,
            "messages_by_author": by_author,
            "all_messages": messages
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print(f"Результаты сохранены в {filename}")
        return result
    
    def print_summary(self, messages: List[Dict]):
        """Выводит краткую сводку"""
        print("\n" + "="*50)
        print("СВОДКА ПО ЗАПИСЯМ СОБЕСЕДОВАНИЙ")
        print("="*50)
        
        # Топ авторов
        authors = {}
        for msg in messages:
            author = msg["author"]
            authors[author] = authors.get(author, 0) + 1
            
        print(f"\nТоп авторов по количеству сообщений:")
        for author, count in sorted(authors.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {author}: {count} сообщений")
            
        # Сообщения с кодом
        code_messages = [msg for msg in messages if msg["has_code"]]
        print(f"\nСообщения с кодом: {len(code_messages)}")
        
        # Сообщения со ссылками
        link_messages = [msg for msg in messages if msg["links"]]
        print(f"Сообщения со ссылками: {len(link_messages)}")
        
        # Популярные ключевые слова
        all_keywords = []
        for msg in messages:
            all_keywords.extend(msg["keywords_found"])
            
        keyword_counts = {}
        for kw in all_keywords:
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
            
        print(f"\nПопулярные ключевые слова:")
        for kw, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {kw}: {count} раз")

def main():
    scraper = TelegramChatScraper()
    
    print("Telegram Chat Scraper - Сбор записей собеседований")
    print("="*60)
    
    # Собираем все сообщения
    all_messages = scraper.collect_all_messages()
    
    if not all_messages:
        print("Не удалось получить сообщения")
        return
    
    # Фильтруем сообщения, связанные с собеседованиями
    interview_messages = scraper.filter_interview_messages(all_messages)
    
    # Сохраняем результаты
    scraper.save_results(interview_messages)
    
    # Выводим сводку
    scraper.print_summary(interview_messages)
    
    # Также сохраняем все сообщения для полного анализа
    scraper.save_results(
        [scraper.structure_message(msg) for msg in all_messages], 
        "all_messages.json"
    )
    
    print(f"\nГотово! Проанализировано {len(all_messages)} сообщений")
    print("Файлы:")
    print("  - interview_records.json - только записи собеседований")
    print("  - all_messages.json - все сообщения чата")

if __name__ == "__main__":
    main() 