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
        # ID сообщений, уже обработанных (скачаны или пропущены по тегу)
        self.processed_ids = set()
        self._load_existing_metadata()

    def _load_existing_metadata(self):
        """Загружает существующий файл метаданных, чтобы возобновлять скачивание"""
        if not self.metadata_file.exists():
            return

        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.posts_data = json.load(f)

            for item in self.posts_data:
                msg_id = item.get("message_id")
                if msg_id is None:
                    continue
                # Уже скачано и файл присутствует
                video_path = item.get("video_path")
                if video_path and os.path.exists(video_path):
                    self.processed_ids.add(msg_id)
                    continue
                # Было пропущено по тегам
                err = str(item.get("download_error", ""))
                if "Skipped" in err:
                    self.processed_ids.add(msg_id)
        except Exception:
            # Если файл повреждён – начинаем заново
            self.posts_data = []
            self.processed_ids = set()
    
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
                        # Искусственная пауза убрана ради ускорения
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
        """Скачивает видео из сообщений параллельно с ограничением по семафору"""
        print(f"\n🎬 Начинаю скачивание видео из {len(messages)} сообщений (параллельно)...")

        # Ограничиваем количество одновременных загрузок
        sem = asyncio.Semaphore(12)

        # Потокобезопасные счётчики статистики
        stats = {
            "downloaded": 0,
            "media": 0,
            "skipped": 0,
            "already": 0,
            "errors": 0,
        }
        counter_lock = asyncio.Lock()

        async def process_message(index: int, message):
            async with sem:
                print(f"\n📝 Обрабатываю сообщение {index}/{len(messages)} (ID: {message.id})")

                # Пропуск, если уже обработано
                if message.id in self.processed_ids:
                    print("⏭️ Уже обработано ранее, пропуск")
                    async with counter_lock:
                        stats["already"] += 1
                    return

                # Предпросмотр текста
                if message.text:
                    preview_text = message.text[:100] + "..." if len(message.text) > 100 else message.text
                    print(f"📄 Текст: {preview_text}")

                # Фильтр по тегам
                if message.text and any(tag in message.text.lower() for tag in ("#vue", "#angular")):
                    print("⏭️ Пропуск: содержит теги #vue/#angular")
                    async with counter_lock:
                        stats["skipped"] += 1
                    self.save_post_data(message, error="Skipped due to Vue/Angular tag")
                    return

                # Нет медиа
                if not message.media:
                    print("📝 Нет медиа файлов")
                    self.save_post_data(message)
                    return

                async with counter_lock:
                    stats["media"] += 1

                media_type = str(type(message.media).__name__)
                print(f"🎯 Найдено медиа: {media_type}")

                try:
                    filename = self.generate_video_filename(message, index)
                    file_path = self.output_dir / filename

                    result = await simple_download_media(self.dialog_id, message.id, str(file_path))

                    if result.get("success"):
                        async with counter_lock:
                            stats["downloaded"] += 1
                        print(f"✅ Скачано: {filename}")
                        self.save_post_data(message, str(file_path))
                    else:
                        async with counter_lock:
                            stats["errors"] += 1
                        err = result.get("error", "Неизвестная ошибка")
                        print(f"❌ Ошибка скачивания: {err}")
                        self.save_post_data(message, error=err)
                except Exception as e:
                    async with counter_lock:
                        stats["errors"] += 1
                    print(f"❌ Исключение при скачивании: {e}")
                    self.save_post_data(message, error=str(e))

        # Собираем задачи и запускаем параллельно
        tasks = [process_message(idx, msg) for idx, msg in enumerate(messages, 1)]
        await asyncio.gather(*tasks)

        # Выводим итоговую статистику
        print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"  📝 Всего сообщений: {len(messages)}")
        print(f"  🎬 С медиа файлами: {stats['media']}")
        print(f"  ⏭️ Пропущено (Vue/Angular): {stats['skipped']}")
        print(f"  🛑 Уже обработано ранее: {stats['already']}")
        print(f"  ✅ Успешно скачано: {stats['downloaded']}")
        print(f"  ❌ Ошибок: {stats['errors']}")
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