"""
Массовое скачивание видео из топика Frontend в ОМ: паравозик собеседований
С связыванием каждого видео с текстом поста от новых к старым
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from src.mcp_telegram.simple_video_downloader import simple_download_media
from src.mcp_telegram.robust_client import get_robust_client

class FrontendVideoDownloader:
    """Загрузчик видео из топика Frontend"""
    
    def __init__(self):
        self.dialog_id = -1002208833410  # ОМ: паравозик собеседований
        self.topic_id = 31  # Frontend топик
        self.output_dir = Path("./frontend_videos")
        self.output_dir.mkdir(exist_ok=True)
        
        # Файл для связки поста и видео
        self.metadata_file = self.output_dir / "posts_and_videos.json"
        self.posts_data = []
    
    async def get_all_topic_messages(self, limit: int = 1000) -> List[Any]:
        """Получает все сообщения из топика Frontend"""
        print(f"📥 Получение сообщений из топика Frontend (лимит: {limit})...")
        
        async with get_robust_client() as client:
            try:
                # Используем метод robust_client для получения сообщений из топика
                async def _get_topic_messages(telethon_client, dialog_id, topic_id, limit):
                    messages = []
                    async for message in telethon_client.iter_messages(
                        entity=dialog_id,
                        limit=limit,
                        reply_to=topic_id,
                        reverse=False  # От новых к старым
                    ):
                        messages.append(message)
                        await asyncio.sleep(0.1)  # Микро-пауза для защиты от блокировки
                    return messages
                
                messages = await client._execute_with_retry(_get_topic_messages, self.dialog_id, self.topic_id, limit)
                
                print(f"✅ Получено {len(messages)} сообщений из топика Frontend")
                return messages
                
            except Exception as e:
                print(f"❌ Ошибка получения сообщений: {e}")
                return []
    
    def save_post_data(self, message, video_path: str = None, error: str = None):
        """Сохраняет данные поста с привязкой к видео"""
        post_data = {
            "message_id": message.id,
            "date": message.date.isoformat() if message.date else None,
            "text": message.text or "",
            "sender_id": getattr(message.sender, 'id', None) if message.sender else None,
            "sender_username": getattr(message.sender, 'username', None) if message.sender else None,
            "sender_first_name": getattr(message.sender, 'first_name', None) if message.sender else None,
            "has_media": bool(message.media),
            "media_type": str(type(message.media).__name__) if message.media else None,
            "video_path": video_path,
            "download_error": error,
            "download_timestamp": datetime.now().isoformat()
        }
        
        self.posts_data.append(post_data)
        
        # Сохраняем данные в файл
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.posts_data, f, ensure_ascii=False, indent=2)
    
    def generate_video_filename(self, message, index: int) -> str:
        """Генерирует имя файла для видео"""
        timestamp = message.date.strftime("%Y%m%d_%H%M%S") if message.date else "unknown"
        return f"frontend_{index:04d}_{timestamp}_{message.id}.mp4"
    
    async def download_videos_from_messages(self, messages: List[Any]):
        """Скачивает видео из сообщений"""
        print(f"\n🎬 Начинаю скачивание видео из {len(messages)} сообщений...")
        
        downloaded_count = 0
        media_count = 0
        error_count = 0
        
        for index, message in enumerate(messages, 1):
            print(f"\n📝 Обрабатываю сообщение {index}/{len(messages)} (ID: {message.id})")
            
            # Показываем текст сообщения
            if message.text:
                preview_text = message.text[:100] + "..." if len(message.text) > 100 else message.text
                print(f"📄 Текст: {preview_text}")
            
            # Проверяем наличие медиа
            if message.media:
                media_count += 1
                media_type = str(type(message.media).__name__)
                print(f"🎯 Найдено медиа: {media_type}")
                
                try:
                    # Генерируем имя файла
                    filename = self.generate_video_filename(message, index)
                    file_path = self.output_dir / filename
                    
                    # Скачиваем медиа
                    result = await simple_download_media(
                        self.dialog_id, 
                        message.id, 
                        str(file_path)
                    )
                    
                    if result.get("success"):
                        downloaded_count += 1
                        print(f"✅ Скачано: {filename}")
                        self.save_post_data(message, str(file_path))
                    else:
                        error_count += 1
                        error_msg = result.get("error", "Неизвестная ошибка")
                        print(f"❌ Ошибка скачивания: {error_msg}")
                        self.save_post_data(message, error=error_msg)
                    
                    # Пауза между скачиваниями для защиты от блокировки
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    error_count += 1
                    print(f"❌ Исключение при скачивании: {e}")
                    self.save_post_data(message, error=str(e))
            else:
                print("📝 Нет медиа файлов")
                self.save_post_data(message)
        
        print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"  📝 Всего сообщений: {len(messages)}")
        print(f"  🎬 С медиа файлами: {media_count}")
        print(f"  ✅ Успешно скачано: {downloaded_count}")
        print(f"  ❌ Ошибок: {error_count}")
        print(f"  📁 Папка: {self.output_dir.absolute()}")
        print(f"  📋 Метаданные: {self.metadata_file.absolute()}")
    
    async def start_download(self, limit: int = 1000):
        """Запускает процесс скачивания"""
        print("🚀 МАССОВОЕ СКАЧИВАНИЕ ВИДЕО ИЗ ТОПИКА FRONTEND")
        print("=" * 60)
        
        # Получаем все сообщения
        messages = await self.get_all_topic_messages(limit)
        if not messages:
            print("❌ Не удалось получить сообщения")
            return
        
        # Скачиваем видео
        await self.download_videos_from_messages(messages)
        
        print("\n🏁 СКАЧИВАНИЕ ЗАВЕРШЕНО!")

async def main():
    """Основная функция"""
    downloader = FrontendVideoDownloader()
    
    # Спрашиваем лимит сообщений
    try:
        limit = int(input("Введите лимит сообщений для обработки (по умолчанию 100): ") or "100")
    except ValueError:
        limit = 100
    
    await downloader.start_download(limit)

if __name__ == "__main__":
    asyncio.run(main()) 