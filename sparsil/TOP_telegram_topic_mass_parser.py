#!/usr/bin/env python3
"""
Массовый парсер сообщений из Telegram темы "Записи собеседований"

Использует расширенный MCP Telegram сервер для извлечения всех 155,797 сообщений
из темы "⚡ Записи собеседований" в супергруппе "Frontend – TO THE JOB"
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Добавляем путь к mcp-telegram модулю
sys.path.insert(0, str(Path("mcp-telegram-main/src").resolve()))

from mcp_telegram.tools import (
    FindTopicByName, 
    tool_runner
)
from mcp_telegram.telegram import create_client

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_parser.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramTopicParser:
    """Класс для массового парсинга сообщений из Telegram темы"""
    
    def __init__(self, dialog_id: int, topic_name: str):
        self.dialog_id = dialog_id
        self.topic_name = topic_name
        self.topic_id: Optional[int] = None
        self.all_messages: List[Dict[str, Any]] = []
        self.batch_size = 100  # Размер пакета для обработки
        
    async def find_topic(self) -> bool:
        """Найти тему по названию"""
        logger.info(f"Поиск темы '{self.topic_name}' в диалоге {self.dialog_id}")
        
        try:
            # Используем наш новый инструмент FindTopicByName
            find_args = FindTopicByName(
                dialog_id=self.dialog_id,
                topic_name=self.topic_name
            )
            
            result = await tool_runner(find_args)
            
            for content in result:
                if content.type == "text" and "FOUND:" in content.text:
                    # Парсим результат: "FOUND: topic_id=123 title='...' ..."
                    parts = content.text.split()
                    for part in parts:
                        if part.startswith("topic_id="):
                            self.topic_id = int(part.split("=")[1])
                            logger.info(f"Найдена тема: ID={self.topic_id}")
                            return True
            
            logger.error(f"Тема '{self.topic_name}' не найдена")
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при поиске темы: {e}")
            return False
    
    async def get_all_topic_messages(self) -> List[Dict[str, Any]]:
        """Получить ВСЕ сообщения из темы с пагинацией"""
        if not self.topic_id:
            raise ValueError("topic_id не найден. Сначала вызовите find_topic()")
        
        logger.info(f"Начинаем извлечение всех сообщений из темы {self.topic_id}")
        
        all_messages = []
        offset_id = 0
        batch_count = 0
        
        # Используем прямое обращение к Telethon для более гибкого управления
        async with create_client() as client:
            while True:
                try:
                    batch_count += 1
                    logger.info(f"Обрабатываем пакет #{batch_count}, offset_id={offset_id}")
                    
                    # Получаем пакет сообщений
                    messages_batch = []
                    async for message in client.iter_messages(
                        entity=self.dialog_id,
                        limit=self.batch_size,
                        offset_id=offset_id,
                        reply_to=self.topic_id  # Фильтр по теме
                    ):
                        if message.text:  # Только текстовые сообщения
                            msg_data = {
                                'id': message.id,
                                'date': message.date.isoformat() if message.date else None,
                                'text': message.text,
                                'from_id': getattr(message.sender, 'id', None) if message.sender else None,
                                'from_username': getattr(message.sender, 'username', None) if message.sender else None,
                                'reply_to_msg_id': getattr(message.reply_to, 'reply_to_msg_id', None) if message.reply_to else None,
                                'topic_id': self.topic_id
                            }
                            messages_batch.append(msg_data)
                    
                    if not messages_batch:
                        logger.info("Больше сообщений нет, завершаем")
                        break
                    
                    all_messages.extend(messages_batch)
                    offset_id = messages_batch[-1]['id']  # ID последнего сообщения для следующего запроса
                    
                    logger.info(f"Получено {len(messages_batch)} сообщений, всего: {len(all_messages)}")
                    
                    # Сохраняем промежуточный результат каждые 10 пакетов
                    if batch_count % 10 == 0:
                        await self.save_intermediate_results(all_messages, batch_count)
                    
                    # Добавляем задержку, чтобы не превысить лимиты API
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Ошибка при получении пакета #{batch_count}: {e}")
                    if "flood" in str(e).lower():
                        logger.warning("Обнаружен flood wait, ждем 60 секунд")
                        await asyncio.sleep(60)
                        continue
                    else:
                        break
        
        logger.info(f"Извлечение завершено. Получено {len(all_messages)} сообщений")
        self.all_messages = all_messages
        return all_messages
    
    async def save_intermediate_results(self, messages: List[Dict[str, Any]], batch_count: int):
        """Сохранить промежуточные результаты"""
        filename = f"telegram_messages_batch_{batch_count}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'topic_name': self.topic_name,
                    'topic_id': self.topic_id,
                    'dialog_id': self.dialog_id,
                    'total_messages': len(messages),
                    'batch_count': batch_count,
                    'timestamp': datetime.now().isoformat(),
                    'messages': messages
                }, f, ensure_ascii=False, indent=2)
            logger.info(f"Промежуточные результаты сохранены в {filename}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении промежуточных результатов: {e}")
    
    async def save_final_results(self, output_file: str = "telegram_topic_messages.json"):
        """Сохранить финальные результаты"""
        if not self.all_messages:
            logger.warning("Нет сообщений для сохранения")
            return
        
        try:
            # JSON файл
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'topic_name': self.topic_name,
                        'topic_id': self.topic_id,
                        'dialog_id': self.dialog_id,
                        'total_messages': len(self.all_messages),
                        'extraction_date': datetime.now().isoformat(),
                        'description': 'Все сообщения из темы "Записи собеседований"'
                    },
                    'messages': self.all_messages
                }, f, ensure_ascii=False, indent=2)
            
            # CSV файл для удобства анализа
            csv_file = output_file.replace('.json', '.csv')
            import csv
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                if self.all_messages:
                    writer = csv.DictWriter(f, fieldnames=self.all_messages[0].keys())
                    writer.writeheader()
                    writer.writerows(self.all_messages)
            
            logger.info(f"Результаты сохранены в {output_file} и {csv_file}")
            logger.info(f"Всего сообщений: {len(self.all_messages)}")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении результатов: {e}")

async def main():
    """Основная функция для запуска парсера"""
    
    # Параметры из предыдущих исследований
    DIALOG_ID = -1002071074234  # ID супергруппы "Frontend – TO THE JOB"
    TOPIC_NAME = "Записи собеседований"  # Название темы для поиска
    
    logger.info("=== Telegram Topic Mass Parser ===")
    logger.info(f"Цель: извлечь все ~155,797 сообщений из темы '{TOPIC_NAME}'")
    logger.info(f"Супергруппа ID: {DIALOG_ID}")
    
    # Проверяем переменные окружения
    if not os.getenv('TELEGRAM_API_ID') or not os.getenv('TELEGRAM_API_HASH'):
        logger.error("Необходимо установить TELEGRAM_API_ID и TELEGRAM_API_HASH")
        sys.exit(1)
    
    # Создаем парсер
    parser = TelegramTopicParser(DIALOG_ID, TOPIC_NAME)
    
    try:
        # Шаг 1: Найти тему
        if not await parser.find_topic():
            logger.error("Не удалось найти тему. Завершение работы.")
            return
        
        # Шаг 2: Получить все сообщения
        messages = await parser.get_all_topic_messages()
        
        # Шаг 3: Сохранить результаты
        await parser.save_final_results()
        
        logger.info("=== Парсинг завершен успешно ===")
        
    except KeyboardInterrupt:
        logger.info("Парсинг прерван пользователем")
        if parser.all_messages:
            await parser.save_final_results("telegram_messages_partial.json")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        if parser.all_messages:
            await parser.save_final_results("telegram_messages_error.json")

if __name__ == "__main__":
    asyncio.run(main()) 