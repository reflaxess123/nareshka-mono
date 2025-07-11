"""
Упрощенный загрузчик видео из Telegram
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from .robust_client import get_robust_client

logger = logging.getLogger(__name__)

class SimpleVideoDownloader:
    """Упрощенный класс для скачивания видео"""

    def __init__(self, download_path: str = "./downloads"):
        self.download_path = Path(download_path)
        self.download_path.mkdir(exist_ok=True)

    def _generate_filename(self, message) -> str:
        """Генерирует имя файла для скачивания"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        msg_id = message.id
        return f"video_{timestamp}_{msg_id}.mp4"

    async def download_video_from_message(
        self,
        dialog_id: int,
        message_id: int,
        custom_path: str | None = None,
    ) -> dict[str, Any]:
        """Скачивает видео из конкретного сообщения"""

        async with get_robust_client() as client:
            try:
                # Получаем сообщение
                message = await client._client.get_messages(dialog_id, ids=message_id)
                if not message:
                    return {"error": "Сообщение не найдено"}

                # Проверяем наличие медиа
                if not message.media:
                    return {"error": "В сообщении нет медиа файлов"}

                # Определяем путь для сохранения
                if custom_path:
                    save_path = Path(custom_path)
                else:
                    filename = self._generate_filename(message)
                    save_path = self.download_path / filename

                # Скачиваем файл
                logger.info(f"Скачивание медиа файла: {save_path}")

                file_path = await client._client.download_media(message.media, file=save_path)

                result = {
                    "success": True,
                    "file_path": str(file_path),
                    "message_id": message_id,
                    "dialog_id": dialog_id,
                    "media_type": str(type(message.media).__name__),
                }

                logger.info(f"Файл скачан: {file_path}")
                return result

            except Exception as e:
                logger.error(f"Ошибка скачивания медиа: {e}")
                return {"error": str(e)}

    async def scan_media_in_dialog(self, dialog_id: int, limit: int = 20) -> list[dict[str, Any]]:
        """Сканирует диалог на наличие медиа файлов"""

        media_list = []

        async with get_robust_client() as client:
            try:
                messages = await client.get_messages(dialog_id, limit=limit)

                for message in messages:
                    if not message.media:
                        continue

                    media_info = {
                        "message_id": message.id,
                        "date": message.date,
                        "media_type": str(type(message.media).__name__),
                        "text": message.text[:100] if message.text else "",
                        "has_media": True,
                    }

                    media_list.append(media_info)

                return media_list

            except Exception as e:
                logger.error(f"Ошибка сканирования медиа: {e}")
                return [{"error": str(e)}]

    async def find_and_download_media(self, dialog_id: int, limit: int = 5) -> list[dict[str, Any]]:
        """Находит и скачивает медиа файлы из диалога"""

        results = []

        async with get_robust_client() as client:
            try:
                # Получаем сообщения
                messages = await client.get_messages(dialog_id, limit=limit * 2)  # Берем больше для фильтрации

                media_count = 0
                for message in messages:
                    if media_count >= limit:
                        break

                    if not message.media:
                        continue

                    # Скачиваем медиа
                    result = await self.download_video_from_message(dialog_id, message.id)
                    if result.get("success"):
                        results.append(result)
                        media_count += 1

                        # Пауза между скачиваниями
                        await asyncio.sleep(1)

                return results

            except Exception as e:
                logger.error(f"Ошибка поиска и скачивания медиа: {e}")
                return [{"error": str(e)}]

# Глобальный экземпляр
simple_downloader = SimpleVideoDownloader()

# Удобные функции
async def simple_download_media(dialog_id: int, message_id: int, path: str | None = None):
    """Скачивает медиа из конкретного сообщения"""
    return await simple_downloader.download_video_from_message(dialog_id, message_id, path)

async def simple_scan_media(dialog_id: int, limit: int = 20):
    """Сканирует диалог на медиа файлы"""
    return await simple_downloader.scan_media_in_dialog(dialog_id, limit)

async def simple_find_and_download(dialog_id: int, limit: int = 5):
    """Находит и скачивает медиа файлы"""
    return await simple_downloader.find_and_download_media(dialog_id, limit)
