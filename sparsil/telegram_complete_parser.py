#!/usr/bin/env python3
"""
ИСПРАВЛЕННЫЙ массовый парсер сообщений из Telegram темы

Использует правильную логику для извлечения ВСЕХ сообщений из темы,
а не только прямых ответов на первое сообщение.
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

from mcp_telegram.telegram import create_client
from telethon import functions, types

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_complete_parser.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def clean_old_sessions():
    """Очистка старых файлов сессий"""
    try:
        session_files = [
            "mcp_telegram_session.session",
            "telegram_session.session", 
            "anon.session"
        ]
        
        # Проверяем в текущей директории
        for session_file in session_files:
            if os.path.exists(session_file):
                os.remove(session_file)
                logger.info(f"Удален старый файл сессии: {session_file}")
        
        # Проверяем в XDG директории
        from xdg_base_dirs import xdg_state_home
        state_home = xdg_state_home() / "mcp-telegram"
        if state_home.exists():
            for session_file in state_home.glob("*.session"):
                session_file.unlink()
                logger.info(f"Удален старый файл сессии: {session_file}")
                
    except Exception as e:
        logger.warning(f"Ошибка при очистке сессий: {e}")

class TelegramCompleteParser:
    """Исправленный класс для ПОЛНОГО парсинга сообщений из Telegram темы"""
    
    def __init__(self, dialog_id: int, topic_id: int):
        self.dialog_id = dialog_id
        self.topic_id = topic_id
        self.all_messages: List[Dict[str, Any]] = []
        self.batch_size = 100
        
        # Получаем API параметры из переменных окружения
        self.api_id = os.getenv('TELEGRAM_API_ID') or os.getenv('TG_APP_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH') or os.getenv('TG_API_HASH')
        
        if not self.api_id or not self.api_hash:
            raise ValueError("Не найдены API параметры! Установите TELEGRAM_API_ID и TELEGRAM_API_HASH")
        
        logger.info(f"API ID: {self.api_id}")
        logger.info(f"API Hash: {self.api_hash[:10]}...")
    

        
    async def get_all_forum_messages_method1(self) -> List[Dict[str, Any]]:
        """Метод 1: Используем GetHistory с правильными параметрами для форума"""
        
        logger.info("=== МЕТОД 1: GetHistory для форума ===")
        all_messages = []
        offset_id = 0
        batch_count = 0
        
        # Используем create_client напрямую с теми же параметрами что в тесте
        client = create_client(
            api_id=self.api_id,
            api_hash=self.api_hash,
            session_name="test_auth_session"
        )
        async with client:
            while True:
                try:
                    batch_count += 1
                    logger.info(f"Пакет #{batch_count}, offset_id={offset_id}")
                    
                    # Используем GetHistory с top_msg_id для фильтрации по теме
                    result = await client(functions.messages.GetHistoryRequest(
                        peer=self.dialog_id,
                        offset_id=offset_id,
                        offset_date=0,
                        add_offset=0,
                        limit=self.batch_size,
                        max_id=0,
                        min_id=0,
                        hash=0,
                        # Ключевой параметр - фильтрация по теме форума
                    ))
                    
                    if not result.messages:
                        logger.info("Больше сообщений нет")
                        break
                    
                    # Фильтруем сообщения по теме
                    topic_messages = []
                    for message in result.messages:
                        # Проверяем, принадлежит ли сообщение к нашей теме
                        if (hasattr(message, 'reply_to') and 
                            message.reply_to and 
                            hasattr(message.reply_to, 'reply_to_msg_id')):
                            
                            # Если это ответ на сообщение из нашей темы
                            if (message.reply_to.reply_to_msg_id == self.topic_id or
                                self.is_message_in_topic(message, all_messages)):
                                topic_messages.append(message)
                        elif (hasattr(message, 'id') and 
                              message.id == self.topic_id):
                            # Само сообщение-тема
                            topic_messages.append(message)
                    
                    # Преобразуем в наш формат
                    batch_messages = []
                    for message in topic_messages:
                        if hasattr(message, 'message') and message.message:
                            msg_data = {
                                'id': message.id,
                                'date': message.date.isoformat() if message.date else None,
                                'text': message.message,
                                'from_id': getattr(message, 'from_id', None),
                                'reply_to_msg_id': getattr(message.reply_to, 'reply_to_msg_id', None) if hasattr(message, 'reply_to') and message.reply_to else None,
                                'topic_id': self.topic_id
                            }
                            batch_messages.append(msg_data)
                    
                    if not batch_messages:
                        logger.info("В пакете нет сообщений из нужной темы")
                        # Но продолжаем, так как могут быть сообщения темы дальше
                        if len(result.messages) < self.batch_size:
                            break
                    
                    all_messages.extend(batch_messages)
                    offset_id = result.messages[-1].id
                    
                    logger.info(f"Получено {len(batch_messages)} сообщений темы, всего: {len(all_messages)}")
                    
                    # Промежуточное сохранение
                    if batch_count % 10 == 0:
                        await self.save_intermediate_results(all_messages, f"method1_batch_{batch_count}")
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Ошибка в пакете #{batch_count}: {e}")
                    if "flood" in str(e).lower():
                        logger.warning("Flood wait, ждем 60 секунд")
                        await asyncio.sleep(60)
                        continue
                    else:
                        break
        
        return all_messages
    
    async def get_all_forum_messages_method2(self) -> List[Dict[str, Any]]:
        """Метод 2: Используем поиск по всем сообщениям с фильтрацией"""
        
        logger.info("=== МЕТОД 2: Полный поиск с фильтрацией ===")
        all_messages = []
        offset_id = 0
        batch_count = 0
        
        # Используем create_client напрямую с теми же параметрами что в тесте
        client = create_client(
            api_id=self.api_id,
            api_hash=self.api_hash,
            session_name="test_auth_session"
        )
        async with client:
            # Сначала получаем все ID сообщений из темы, используя существующий метод
            logger.info("Получаем базовый список ID сообщений темы...")
            base_messages = []
            async for message in client.iter_messages(
                entity=self.dialog_id,
                limit=None,  # Получаем все
                reply_to=self.topic_id
            ):
                if message.text:
                    base_messages.append(message.id)
            
            logger.info(f"Найдено {len(base_messages)} базовых сообщений")
            
            # Теперь ищем сообщения, которые могут быть ответами на эти сообщения
            all_topic_ids = set(base_messages + [self.topic_id])
            
            # Проходим по всем сообщениям в чате и ищем связанные с темой
            offset_id = 0
            while True:
                try:
                    batch_count += 1
                    logger.info(f"Сканируем пакет #{batch_count}, offset_id={offset_id}")
                    
                    batch_messages = []
                    async for message in client.iter_messages(
                        entity=self.dialog_id,
                        limit=self.batch_size,
                        offset_id=offset_id
                    ):
                        if message.text:
                            # Проверяем, связано ли сообщение с нашей темой
                            is_topic_message = False
                            
                            # 1. Прямой ответ на сообщение темы
                            if (hasattr(message, 'reply_to') and message.reply_to and
                                hasattr(message.reply_to, 'reply_to_msg_id') and
                                message.reply_to.reply_to_msg_id in all_topic_ids):
                                is_topic_message = True
                                all_topic_ids.add(message.id)  # Добавляем для дальнейшего поиска
                            
                            # 2. Само сообщение-основа темы
                            elif message.id == self.topic_id:
                                is_topic_message = True
                            
                            if is_topic_message:
                                msg_data = {
                                    'id': message.id,
                                    'date': message.date.isoformat() if message.date else None,
                                    'text': message.message,
                                    'from_id': getattr(message, 'from_id', None),
                                    'reply_to_msg_id': getattr(message.reply_to, 'reply_to_msg_id', None) if hasattr(message, 'reply_to') and message.reply_to else None,
                                    'topic_id': self.topic_id
                                }
                                batch_messages.append(msg_data)
                    
                    if not batch_messages:
                        logger.info("В пакете нет новых сообщений темы")
                        if batch_count > 50:  # Ограничение для безопасности
                            break
                    else:
                        all_messages.extend(batch_messages)
                        logger.info(f"Найдено {len(batch_messages)} сообщений темы, всего: {len(all_messages)}")
                    
                    # Промежуточное сохранение
                    if batch_count % 20 == 0:
                        await self.save_intermediate_results(all_messages, f"method2_batch_{batch_count}")
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Ошибка в пакете #{batch_count}: {e}")
                    break
        
        return all_messages
    
    def is_message_in_topic(self, message, existing_messages):
        """Проверяет, принадлежит ли сообщение к теме"""
        # Простая эвристика - если это ответ на любое из уже найденных сообщений темы
        if not hasattr(message, 'reply_to') or not message.reply_to:
            return False
        
        reply_to_id = getattr(message.reply_to, 'reply_to_msg_id', None)
        if not reply_to_id:
            return False
        
        # Проверяем, есть ли сообщение с таким ID среди уже найденных
        return any(msg['id'] == reply_to_id for msg in existing_messages)
    
    async def save_intermediate_results(self, messages: List[Dict[str, Any]], suffix: str):
        """Сохранить промежуточные результаты"""
        filename = f"telegram_complete_{suffix}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'topic_id': self.topic_id,
                    'dialog_id': self.dialog_id,
                    'total_messages': len(messages),
                    'timestamp': datetime.now().isoformat(),
                    'messages': messages
                }, f, ensure_ascii=False, indent=2)
            logger.info(f"Промежуточные результаты сохранены в {filename}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении: {e}")
    
    async def save_final_results(self, messages: List[Dict[str, Any]], filename: str = "telegram_complete_messages.json"):
        """Сохранить финальные результаты"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'topic_id': self.topic_id,
                        'dialog_id': self.dialog_id,
                        'total_messages': len(messages),
                        'extraction_date': datetime.now().isoformat(),
                        'description': 'ПОЛНЫЙ набор сообщений из темы с исправленным алгоритмом'
                    },
                    'messages': messages
                }, f, ensure_ascii=False, indent=2)
            
            # CSV файл
            csv_file = filename.replace('.json', '.csv')
            import csv
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                if messages:
                    writer = csv.DictWriter(f, fieldnames=messages[0].keys())
                    writer.writeheader()
                    writer.writerows(messages)
            
            logger.info(f"Результаты сохранены в {filename} и {csv_file}")
            logger.info(f"Всего сообщений: {len(messages)}")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении: {e}")

async def main():
    """Основная функция"""
    
    DIALOG_ID = -1002071074234
    TOPIC_ID = 489
    
    logger.info("=== ИСПРАВЛЕННЫЙ Telegram Topic Parser ===")
    logger.info(f"Цель: получить ВСЕ сообщения из темы {TOPIC_ID}")
    
    # НЕ очищаем сессии - используем существующую аутентификацию
    logger.info("Используем существующую сессию...")
    
    parser = TelegramCompleteParser(DIALOG_ID, TOPIC_ID)
    
    try:
        # Пробуем метод 2 - более надежный
        logger.info("Запускаем МЕТОД 2 (полный поиск)...")
        messages = await parser.get_all_forum_messages_method2()
        
        # Сохраняем результаты
        await parser.save_final_results(messages)
        
        logger.info(f"=== ЗАВЕРШЕНО: Найдено {len(messages)} сообщений ===")
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 