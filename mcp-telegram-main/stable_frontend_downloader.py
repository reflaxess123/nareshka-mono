"""
СТАБИЛЬНОЕ СКАЧИВАНИЕ ВИДЕО ИЗ ТОПИКА FRONTEND
Небольшими порциями с защитой от зависания и возможностью продолжения
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from src.mcp_telegram.robust_client import get_robust_client
from src.mcp_telegram.simple_video_downloader import simple_download_media


class StableFrontendDownloader:
    """Стабильный загрузчик видео из топика Frontend"""

    def __init__(self, batch_size: int = 5):
        self.dialog_id = -1002208833410  # ОМ: паравозик собеседований
        self.topic_id = 31  # Frontend топик
        self.batch_size = batch_size  # Размер пакета для скачивания
        self.output_dir = Path("./frontend_videos_stable")
        self.output_dir.mkdir(exist_ok=True)

        # Файлы для отслеживания
        self.metadata_file = self.output_dir / "downloaded_videos.json"
        self.progress_file = self.output_dir / "download_progress.json"
        self.downloaded_ids = set()  # Уже скачанные ID

        # Загружаем уже скачанные ID
        self.load_downloaded_ids()

    def load_downloaded_ids(self):
        """Загружает ID уже скачанных видео"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self.downloaded_ids = set(
                        item["message_id"] for item in data
                        if item.get("success", False)
                    )
                print(f"📂 Загружено {len(self.downloaded_ids)} уже скачанных видео")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки истории: {e}")
                self.downloaded_ids = set()

    def save_metadata(self, new_results: list[dict[str, Any]]):
        """Добавляет новые результаты к метаданным"""
        existing_data = []

        # Загружаем существующие данные
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, encoding="utf-8") as f:
                    existing_data = json.load(f)
            except Exception as e:
                print(f"⚠️ Ошибка загрузки метаданных: {e}")

        # Добавляем новые результаты
        for result in new_results:
            message_info = result["message_info"]
            message = message_info["message"]

            post_data = {
                "message_id": message.id,
                "date": message.date.isoformat() if message.date else None,
                "text": message_info["text"],
                "sender_id": getattr(message.sender, "id", None) if message.sender else None,
                "sender_username": getattr(message.sender, "username", None) if message.sender else None,
                "media_type": message_info["media_type"],
                "estimated_size": message_info["estimated_size"],
                "success": result["success"],
                "filename": result.get("filename"),
                "file_path": result.get("file_path"),
                "actual_size": result.get("size"),
                "download_time": result.get("download_time"),
                "error": result.get("error"),
                "download_timestamp": datetime.now().isoformat(),
            }

            existing_data.append(post_data)

        # Сохраняем обновленные данные
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

    def save_progress(self, current_batch: int, total_batches: int, batch_results: list[dict[str, Any]]):
        """Сохраняет прогресс скачивания"""
        successful = sum(1 for r in batch_results if r["success"])
        failed = len(batch_results) - successful

        progress_data = {
            "current_batch": current_batch,
            "total_batches": total_batches,
            "batch_size": self.batch_size,
            "batch_successful": successful,
            "batch_failed": failed,
            "total_downloaded": len(self.downloaded_ids),
            "timestamp": datetime.now().isoformat(),
        }

        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)

    def format_size(self, size_bytes: int) -> str:
        """Форматирует размер в человекочитаемом виде"""
        if size_bytes == 0:
            return "0 B"

        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def format_time(self, seconds: float) -> str:
        """Форматирует время"""
        if seconds < 60:
            return f"{seconds:.1f}с"
        if seconds < 3600:
            return f"{int(seconds // 60)}м {int(seconds % 60)}с"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}ч {minutes}м"

    def generate_filename(self, message_info: dict[str, Any], index: int) -> str:
        """Генерирует имя файла для видео"""
        message = message_info["message"]
        timestamp = message.date.strftime("%Y%m%d_%H%M%S") if message.date else "unknown"
        return f"frontend_{index:04d}_{timestamp}_{message.id}.mp4"

    async def get_messages_batch(self, limit: int = 50) -> list[dict[str, Any]]:
        """Получает пакет сообщений для скачивания"""
        print(f"📥 Получение сообщений из топика Frontend (лимит: {limit})...")

        async with get_robust_client() as client:
            try:
                async def _get_topic_messages(telethon_client, dialog_id, topic_id, limit):
                    messages = []
                    async for message in telethon_client.iter_messages(
                        entity=dialog_id,
                        limit=limit,
                        reply_to=topic_id,
                        reverse=False,
                    ):
                        # Пропускаем уже скачанные
                        if message.id in self.downloaded_ids:
                            continue

                        # Только с медиа
                        if not message.media:
                            continue

                        # Собираем информацию о сообщении
                        message_info = {
                            "message": message,
                            "id": message.id,
                            "date": message.date,
                            "text": message.text or "",
                            "has_media": bool(message.media),
                            "media_type": str(type(message.media).__name__) if message.media else None,
                            "estimated_size": 0,
                        }

                        # Получаем размер медиа файла
                        if message.media and hasattr(message.media, "document"):
                            if hasattr(message.media.document, "size"):
                                message_info["estimated_size"] = message.media.document.size

                        messages.append(message_info)
                        await asyncio.sleep(0.05)

                    return messages

                messages = await client._execute_with_retry(_get_topic_messages, self.dialog_id, self.topic_id, limit)

                total_size = sum(msg["estimated_size"] for msg in messages)

                print(f"✅ Получено {len(messages)} новых сообщений с медиа")
                print(f"📊 Размер пакета: {self.format_size(total_size)}")

                return messages

            except Exception as e:
                print(f"❌ Ошибка получения сообщений: {e}")
                return []

    async def download_single_video(self, message_info: dict[str, Any], index: int) -> dict[str, Any]:
        """Скачивает одно видео"""
        message = message_info["message"]
        filename = self.generate_filename(message_info, index)
        file_path = self.output_dir / filename

        # Проверяем, что файл не существует
        if file_path.exists():
            print(f"⚠️ Файл уже существует: {filename}")
            return {
                "success": False,
                "error": "Файл уже существует",
                "message_info": message_info,
            }

        download_start = time.time()

        try:
            print(f"🎬 Скачиваю: {filename}")
            preview_text = message_info["text"][:80] + "..." if len(message_info["text"]) > 80 else message_info["text"]
            print(f"   📄 {preview_text}")
            print(f"   📊 {self.format_size(message_info['estimated_size'])}")

            # Скачиваем медиа с таймаутом
            result = await asyncio.wait_for(
                simple_download_media(self.dialog_id, message.id, str(file_path)),
                timeout=300,  # 5 минут таймаут
            )

            download_time = time.time() - download_start

            if result.get("success"):
                # Получаем реальный размер файла
                actual_size = file_path.stat().st_size if file_path.exists() else 0
                speed = actual_size / download_time if download_time > 0 else 0

                print(f"   ✅ Скачано за {self.format_time(download_time)}")
                print(f"   🚀 Скорость: {self.format_size(speed)}/с")
                print(f"   📁 Размер: {self.format_size(actual_size)}")

                # Добавляем в список скачанных
                self.downloaded_ids.add(message.id)

                return {
                    "success": True,
                    "filename": filename,
                    "file_path": str(file_path),
                    "size": actual_size,
                    "download_time": download_time,
                    "message_info": message_info,
                }
            error_msg = result.get("error", "Неизвестная ошибка")
            print(f"   ❌ Ошибка: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "message_info": message_info,
            }

        except TimeoutError:
            print("   ⏰ Таймаут (5 минут)")
            return {
                "success": False,
                "error": "Таймаут скачивания",
                "message_info": message_info,
            }
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
            return {
                "success": False,
                "error": str(e),
                "message_info": message_info,
            }

    async def download_batch(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Скачивает пакет видео последовательно"""
        results = []

        for i, message_info in enumerate(messages):
            result = await self.download_single_video(message_info, i + 1)
            results.append(result)

            # Пауза между скачиваниями
            await asyncio.sleep(1)

        return results

    async def start_download(self, total_limit: int = 50):
        """Запускает процесс скачивания пакетами"""
        print("🚀 СТАБИЛЬНОЕ СКАЧИВАНИЕ ВИДЕО ИЗ ТОПИКА FRONTEND")
        print("=" * 60)

        total_downloaded = 0
        batch_num = 0

        while total_downloaded < total_limit:
            batch_num += 1
            remaining = total_limit - total_downloaded
            batch_limit = min(self.batch_size, remaining)

            print(f"\n📦 ПАКЕТ {batch_num} (лимит: {batch_limit})")
            print("=" * 40)

            # Получаем пакет сообщений
            messages = await self.get_messages_batch(batch_limit)

            if not messages:
                print("✅ Нет новых сообщений для скачивания")
                break

            # Скачиваем пакет
            batch_start = time.time()
            results = await self.download_batch(messages)
            batch_time = time.time() - batch_start

            # Сохраняем результаты
            self.save_metadata(results)

            # Статистика пакета
            successful = sum(1 for r in results if r["success"])
            failed = len(results) - successful
            total_downloaded += successful

            print(f"\n📊 ПАКЕТ {batch_num} ЗАВЕРШЕН:")
            print(f"   ✅ Успешно: {successful}")
            print(f"   ❌ Ошибок: {failed}")
            print(f"   ⏱️ Время: {self.format_time(batch_time)}")
            print(f"   📈 Всего скачано: {total_downloaded}")

            # Сохраняем прогресс
            self.save_progress(batch_num, -1, results)

            # Пауза между пакетами
            if total_downloaded < total_limit:
                print("⏸️ Пауза 5 секунд...")
                await asyncio.sleep(5)

        print("\n🏁 СКАЧИВАНИЕ ЗАВЕРШЕНО!")
        print(f"   📊 Всего скачано: {total_downloaded}")
        print(f"   📁 Папка: {self.output_dir.absolute()}")

async def main():
    """Основная функция"""
    print("🎬 СТАБИЛЬНОЕ СКАЧИВАНИЕ ВИДЕО ИЗ ТОПИКА FRONTEND")
    print("Рекомендуется начинать с небольших порций!")

    try:
        batch_size = int(input("Размер пакета (по умолчанию 5): ") or "5")
        batch_size = max(1, min(batch_size, 10))  # Ограничиваем от 1 до 10
    except ValueError:
        batch_size = 5

    try:
        total_limit = int(input("Общий лимит видео (по умолчанию 20): ") or "20")
        total_limit = max(1, min(total_limit, 100))  # Ограничиваем от 1 до 100
    except ValueError:
        total_limit = 20

    downloader = StableFrontendDownloader(batch_size=batch_size)
    await downloader.start_download(total_limit)

if __name__ == "__main__":
    asyncio.run(main())
