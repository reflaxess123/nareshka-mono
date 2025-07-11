"""
Упрощенный загрузчик видео из Telegram
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from .robust_client import get_robust_client
from tqdm import tqdm  # Добавляем отображение прогресса

logger = logging.getLogger(__name__)

# Увеличиваем количество соединений и размер чанка для радикального ускорения
MAX_WORKERS = 32  # Было 8
PART_SIZE = 4 * 1024 * 1024  # 4 МБ вместо 512 КБ

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
                    display_name = Path(custom_path).name
                else:
                    filename = self._generate_filename(message)
                    save_path = self.download_path / filename
<<<<<<< HEAD
                    display_name = filename

                # Скачиваем файл с прогресс-баром
                logger.info(f"Скачивание медиа файла: {save_path}")

                # Используем message_id для распределения строк прогресса, чтобы не мешать друг другу
                bar_position = message.id % 10  # до 10 одновременных строк

                with tqdm(
                    total=0,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=display_name,
                    leave=False,
                    position=bar_position,
                ) as progress_bar:

                    def _progress(current: int, total: int):  # noqa: ANN001
                        # Устанавливаем общий размер, когда станет известен
                        if total and progress_bar.total == 0:
                            progress_bar.total = total
                        # Обновляем дельту, а не абсолютное значение
                        progress_bar.update(current - progress_bar.n)

                    # Формируем kwargs только если параметры поддерживаются текущей версией Telethon
                    import inspect

                    dm_sig = inspect.signature(client._client.download_media)
                    extra_kwargs = {}
                    if 'part_size' in dm_sig.parameters:
                        extra_kwargs['part_size'] = PART_SIZE
                    if 'workers' in dm_sig.parameters:
                        extra_kwargs['workers'] = MAX_WORKERS

                    # Пытаемся использовать download_file с крупными блоками (1 МБ) — быстрее
                    try:
                        if hasattr(message.media, 'document') and message.media.document:
                            # Собираем kwargs с учётом поддержки параметров текущей версии Telethon
                            df_sig = inspect.signature(client._client.download_file)
                            df_kwargs = {
                                "file": save_path,
                                "part_size_kb": 1024,  # мелкие чанки для частого прогресса
                                "progress_callback": _progress,
                            }
                            if "threads" in df_sig.parameters:
                                df_kwargs["threads"] = 16

                            file_path = await client._client.download_file(
                                message.media.document,
                                **df_kwargs,
                            )
                        else:
                            # Fallback для других типов медиа
                            file_path = await client._client.download_media(
                                message.media,
                                file=save_path,
                                progress_callback=_progress,
                            )
                    except Exception as dl_e:
                        # При ошибке пробуем стандартный способ
                        logger.warning(f"download_file не удался ({dl_e}), пробую download_media")
                        file_path = await client._client.download_media(
                            message.media,
                            file=save_path,
                            progress_callback=_progress,
                        )
                
                logger.info(f"Файл скачан: {file_path}")
                
=======

                # Скачиваем файл
                logger.info(f"Скачивание медиа файла: {save_path}")

                file_path = await client._client.download_media(message.media, file=save_path)

>>>>>>> 05a40047f43b38854814fce3ae26b69ba4fb7c32
                result = {
                    "success": True,
                    "file_path": str(file_path),
                    "message_id": message_id,
                    "dialog_id": dialog_id,
                    "media_type": str(type(message.media).__name__),
                }
<<<<<<< HEAD
                
=======

                logger.info(f"Файл скачан: {file_path}")
>>>>>>> 05a40047f43b38854814fce3ae26b69ba4fb7c32
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
