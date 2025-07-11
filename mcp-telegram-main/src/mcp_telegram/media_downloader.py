"""
Скачивание видео и медиа файлов из Telegram
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

# Исправляем импорты для работы с telethon
try:
    from telethon.tl.types import (
        DocumentAttributeFilename,
        DocumentAttributeVideo,
        MessageMediaDocument,
        MessageMediaPhoto,
        MessageMediaVideo,
    )
except ImportError:
    # Fallback для разных версий telethon
    from telethon.tl.types import (
        DocumentAttributeFilename,
        DocumentAttributeVideo,
        MessageMediaDocument,
        MessageMediaPhoto,
        MessageMediaVideo,
    )

from .robust_client import get_robust_client

logger = logging.getLogger(__name__)

class MediaDownloader:
    """Класс для скачивания медиа файлов из Telegram"""

    def __init__(self, download_path: str = "./downloads"):
        self.download_path = Path(download_path)
        self.download_path.mkdir(exist_ok=True)

    def _get_media_info(self, message) -> dict[str, Any]:
        """Получает информацию о медиа файле"""
        if not message.media:
            return {"type": "none", "size": 0, "filename": None}

        media_info = {
            "type": "unknown",
            "size": 0,
            "filename": None,
            "duration": None,
            "width": None,
            "height": None,
        }

        if isinstance(message.media, MessageMediaVideo):
            media_info["type"] = "video"
            if message.media.video:
                media_info["size"] = message.media.video.size
                media_info["duration"] = message.media.video.duration

                # Ищем атрибуты видео
                for attr in message.media.video.attributes:
                    if isinstance(attr, DocumentAttributeVideo):
                        media_info["width"] = attr.w
                        media_info["height"] = attr.h
                    elif isinstance(attr, DocumentAttributeFilename):
                        media_info["filename"] = attr.file_name

        elif isinstance(message.media, MessageMediaPhoto):
            media_info["type"] = "photo"
            if message.media.photo:
                media_info["size"] = sum(size.size for size in message.media.photo.sizes)

        elif isinstance(message.media, MessageMediaDocument):
            if message.media.document:
                media_info["size"] = message.media.document.size
                media_info["type"] = "document"

                # Определяем тип документа
                if message.media.document.mime_type:
                    if message.media.document.mime_type.startswith("video/"):
                        media_info["type"] = "video"
                    elif message.media.document.mime_type.startswith("image/"):
                        media_info["type"] = "photo"
                    elif message.media.document.mime_type.startswith("audio/"):
                        media_info["type"] = "audio"

                # Ищем имя файла
                for attr in message.media.document.attributes:
                    if isinstance(attr, DocumentAttributeFilename):
                        media_info["filename"] = attr.file_name
                    elif isinstance(attr, DocumentAttributeVideo):
                        media_info["duration"] = attr.duration
                        media_info["width"] = attr.w
                        media_info["height"] = attr.h

        return media_info

    def _generate_filename(self, message, media_info: dict[str, Any]) -> str:
        """Генерирует имя файла для скачивания"""
        if media_info["filename"]:
            return media_info["filename"]

        # Генерируем имя на основе типа и времени
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        msg_id = message.id

        extensions = {
            "video": ".mp4",
            "photo": ".jpg",
            "audio": ".mp3",
            "document": ".bin",
        }

        ext = extensions.get(media_info["type"], ".bin")
        return f"{media_info['type']}_{timestamp}_{msg_id}{ext}"

    async def download_media_from_message(
        self,
        dialog_id: int,
        message_id: int,
        custom_path: str | None = None,
    ) -> dict[str, Any]:
        """Скачивает медиа файл из конкретного сообщения"""

        async with get_robust_client() as client:
            try:
                # Получаем сообщение
                message = await client._client.get_messages(dialog_id, ids=message_id)
                if not message:
                    return {"error": "Сообщение не найдено"}

                # Проверяем наличие медиа
                media_info = self._get_media_info(message)
                if media_info["type"] == "none":
                    return {"error": "В сообщении нет медиа файлов"}

                # Определяем путь для сохранения
                if custom_path:
                    save_path = Path(custom_path)
                else:
                    filename = self._generate_filename(message, media_info)
                    save_path = self.download_path / filename

                # Скачиваем файл
                logger.info(f"Скачивание {media_info['type']} файла: {save_path}")

                file_path = await client._client.download_media(message.media, file=save_path)

                result = {
                    "success": True,
                    "file_path": str(file_path),
                    "media_info": media_info,
                    "message_id": message_id,
                    "dialog_id": dialog_id,
                }

                logger.info(f"Файл скачан: {file_path}")
                return result

            except Exception as e:
                logger.error(f"Ошибка скачивания медиа: {e}")
                return {"error": str(e)}

    async def find_and_download_videos(
        self,
        dialog_id: int,
        limit: int = 10,
        min_duration: int = 0,
    ) -> list[dict[str, Any]]:
        """Находит и скачивает видео файлы из диалога"""

        results = []

        async with get_robust_client() as client:
            try:
                # Получаем сообщения
                messages = await client.get_messages(dialog_id, limit=limit * 3)  # Берем больше для фильтрации

                video_count = 0
                for message in messages:
                    if video_count >= limit:
                        break

                    if not message.media:
                        continue

                    media_info = self._get_media_info(message)

                    # Фильтруем только видео
                    if media_info["type"] != "video":
                        continue

                    # Проверяем минимальную длительность
                    if media_info["duration"] and media_info["duration"] < min_duration:
                        continue

                    # Скачиваем видео
                    result = await self.download_media_from_message(dialog_id, message.id)
                    if result.get("success"):
                        results.append(result)
                        video_count += 1

                        # Пауза между скачиваниями
                        await asyncio.sleep(1)

                return results

            except Exception as e:
                logger.error(f"Ошибка поиска и скачивания видео: {e}")
                return [{"error": str(e)}]

    async def scan_media_in_dialog(self, dialog_id: int, limit: int = 50) -> list[dict[str, Any]]:
        """Сканирует диалог на наличие медиа файлов"""

        media_list = []

        async with get_robust_client() as client:
            try:
                messages = await client.get_messages(dialog_id, limit=limit)

                for message in messages:
                    if not message.media:
                        continue

                    media_info = self._get_media_info(message)
                    if media_info["type"] != "none":
                        media_list.append({
                            "message_id": message.id,
                            "date": message.date,
                            "media_info": media_info,
                            "text": message.text[:100] if message.text else "",
                        })

                return media_list

            except Exception as e:
                logger.error(f"Ошибка сканирования медиа: {e}")
                return [{"error": str(e)}]

# Глобальный экземпляр
media_downloader = MediaDownloader()

# Удобные функции
async def download_video_from_message(dialog_id: int, message_id: int, path: str | None = None):
    """Скачивает видео из конкретного сообщения"""
    return await media_downloader.download_media_from_message(dialog_id, message_id, path)

async def find_videos_in_dialog(dialog_id: int, limit: int = 10, min_duration: int = 0):
    """Находит видео в диалоге"""
    return await media_downloader.find_and_download_videos(dialog_id, limit, min_duration)

async def scan_dialog_media(dialog_id: int, limit: int = 50):
    """Сканирует диалог на медиа файлы"""
    return await media_downloader.scan_media_in_dialog(dialog_id, limit)
