"""
ИДЕАЛЬНЫЙ СКАЧИВАТЕЛЬ ВИДЕО
Объединяет все лучшие функции:
- Скачивание по одному файлу
- Прогресс-бар со скоростью
- Пропуск уже скачанных
- Фильтрация angular/vue
- Автоматический переход к следующему файлу
- Оптимизированная скорость
- Множественные методы скачивания
"""

import asyncio
import json
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Используем прямое подключение для максимальной скорости


class PerfectDownloader:
    """Идеальный скачиватель видео"""

    def __init__(self):
        self.dialog_id = -1002208833410
        self.topic_id = 31
        self.output_dir = Path("./frontend_media")
        self.output_dir.mkdir(exist_ok=True)
        
        # Файл для отслеживания скачанных
        self.metadata_file = self.output_dir / "downloads.json"
        self.downloaded_ids = set()
        self.load_downloaded_ids()
        
        # Фильтр для пропуска angular/vue
        self.skip_keywords = [
            'angular', 'vue', 'vuejs', 'vue.js', 'nuxt', 
            'angular2', 'angular4', 'angular5', 'angular6', 'angular7', 
            'angular8', 'angular9', 'angular10', 'angular11', 'angular12',
            'angular13', 'angular14', 'angular15', 'angular16', 'angular17',
            'ng-', 'ngrx', 'angular cli', 'angular material'
        ]
        
        # Статистика
        self.total_downloaded = 0
        self.total_size = 0
        self.start_time = time.time()
        
        # Сохраняем клиент для переиспользования
        self.client = None

    def load_downloaded_ids(self):
        """Загружает ID уже скачанных файлов из папки и JSON"""
        self.downloaded_ids = set()
        
        # Проверяем ВСЕ медиа файлы в папке (видео и аудио)
        if self.output_dir.exists():
            media_files = list(self.output_dir.glob("*.mp4")) + list(self.output_dir.glob("*.mp3"))
            for media_file in media_files:
                # Извлекаем message_id из имени файла
                # Поддерживаем разные форматы:
                # - frontend_20250625_134905_3611.mp4
                # - VK_React_Typescript_Frontend_2025-06-25_3612.mp4
                parts = media_file.stem.split('_')
                if len(parts) >= 2:
                    try:
                        # Последняя часть - это message_id
                        message_id = int(parts[-1])
                        self.downloaded_ids.add(message_id)
                    except ValueError:
                        continue
            
            print(f"Found {len(media_files)} media files in folder")
        
        # Дополнительно проверяем JSON файл для консистентности
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, encoding="utf-8") as f:
                    data = json.load(f)
                    json_ids = set(
                        item["message_id"] for item in data
                        if item.get("success", False)
                    )
                    # Объединяем ID из папки и JSON
                    self.downloaded_ids.update(json_ids)
                    print(f"Added {len(json_ids)} IDs from metadata file")
            except Exception as e:
                print(f"Error loading metadata: {e}")
        
        print(f"Total downloaded IDs: {len(self.downloaded_ids)}")
        
        # Показываем размер уже скачанных файлов
        if self.output_dir.exists():
            mp4_files = list(self.output_dir.glob("*.mp4"))
            mp3_files = list(self.output_dir.glob("*.mp3"))
            total_size = sum(f.stat().st_size for f in mp4_files + mp3_files)
            if total_size > 0:
                print(f"Total size of downloaded files: {self.format_size(total_size)}")

    def save_result(self, result: dict[str, Any]):
        """Сохраняет результат скачивания"""
        existing_data = []
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, encoding="utf-8") as f:
                    existing_data = json.load(f)
            except Exception:
                pass

        existing_data.append(result)
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

    def should_skip(self, text: str) -> bool:
        """Проверяет нужно ли пропустить по ключевым словам"""
        text_lower = text.lower()
        for keyword in self.skip_keywords:
            if keyword in text_lower:
                return True
        return False

    def format_size(self, size_bytes: int) -> str:
        """Форматирует размер"""
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
            return f"{seconds:.1f}s"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"

    def extract_company_name(self, text: str) -> str:
        """Извлекает название компании из текста"""
        import re
        # Ищем после "Компания" или "компания"
        patterns = [
            r'компания\s*[-–]\s*#?([^#\n]+)',
            r'компания\s*[-–]\s*([^#\n]+)',
            r'#([A-Za-zА-Яа-я0-9_]+)',  # Хэштег компании
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                # Убираем лишние символы
                company = re.sub(r'[#\s]+', '_', company)
                company = re.sub(r'[^\w\-_]', '', company)
                return company[:15]  # Ограничиваем длину
        
        return "Unknown"

    def extract_tech_stack(self, text: str) -> str:
        """Извлекает технологии из текста"""
        tech_keywords = [
            'react', 'vue', 'angular', 'typescript', 'javascript', 
            'node', 'python', 'java', 'php', 'go', 'rust',
            'frontend', 'backend', 'fullstack'
        ]
        
        found_tech = []
        text_lower = text.lower()
        
        for tech in tech_keywords:
            if tech in text_lower:
                found_tech.append(tech.capitalize())
        
        return '_'.join(found_tech[:2]) if found_tech else "Frontend"

    def generate_filename(self, message) -> str:
        """Генерирует нормальное имя файла"""
        import re
        
        text = message.text or ""
        company = self.extract_company_name(text)
        tech = self.extract_tech_stack(text)
        date = message.date.strftime("%Y-%m-%d") if message.date else "unknown"
        message_id = message.id
        
        # Определяем расширение по типу медиа
        extension = ".mp4"  # По умолчанию видео
        if hasattr(message.media, 'document') and message.media.document:
            if hasattr(message.media.document, 'mime_type'):
                mime_type = message.media.document.mime_type.lower()
                if mime_type.startswith('audio/'):
                    extension = ".mp3"
                elif mime_type.startswith('video/'):
                    extension = ".mp4"
                elif 'audio' in mime_type:
                    extension = ".mp3"
                elif 'video' in mime_type:
                    extension = ".mp4"
        
        # Создаем нормальное имя
        filename = f"{company}_{tech}_{date}_{message_id}{extension}"
        
        # Очищаем от невалидных символов
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        return filename

    def progress_callback(self, current: int, total: int):
        """Быстрый прогресс-бар с оптимизацией"""
        if not hasattr(self, '_download_start'):
            return
            
        current_time = time.time()
        
        # Обновляем каждые 1 секунду для более актуальной информации
        if not hasattr(self, '_last_progress_update'):
            self._last_progress_update = current_time
        elif current_time - self._last_progress_update < 1.0:
            return
            
        self._last_progress_update = current_time
            
        if total > 0:
            progress = (current / total) * 100
            elapsed = current_time - self._download_start
            speed = current / elapsed if elapsed > 0 else 0
            
            # ETA
            if speed > 0:
                eta = (total - current) / speed
                eta_str = self.format_time(eta)
            else:
                eta_str = "unknown"
            
            # Компактный прогресс бар
            bar_length = 25
            filled = int(bar_length * current / total)
            bar = '=' * filled + '-' * (bar_length - filled)
            
            print(f"\r[{bar}] {progress:.1f}% | {self.format_size(speed)}/s | ETA: {eta_str}", end="")

    async def find_next_video(self) -> dict[str, Any] | None:
        """Находит следующий видео для скачивания"""
        try:
            # Используем уже авторизованный клиент для поиска
            from src.mcp_telegram.telegram import create_client
            
            client = create_client()
            await client.connect()
            
            # Оптимизируем для быстрого поиска
            client.flood_sleep_threshold = 0
            if hasattr(client, '_flood_sleep_threshold'):
                client._flood_sleep_threshold = 0
            
            try:
                async for message in client.iter_messages(
                    entity=self.dialog_id,
                    limit=1000,  # Увеличиваем лимит поиска
                    reply_to=self.topic_id,
                    reverse=False,
                ):
                    # Пропускаем уже скачанные
                    if message.id in self.downloaded_ids:
                        continue
                    
                    # Только медиа файлы
                    if not message.media:
                        continue
                    
                    # Проверяем на angular/vue
                    text = message.text or ""
                    if self.should_skip(text):
                        continue
                    
                    # Получаем размер
                    size = 0
                    if hasattr(message.media, "document") and hasattr(message.media.document, "size"):
                        size = message.media.document.size
                    
                    return {
                        "message": message,
                        "text": text,
                        "size": size,
                        "media_type": str(type(message.media).__name__)
                    }
                
                return None
                
            finally:
                await client.disconnect()

        except Exception as e:
            print(f"Error finding video: {e}")
            return None

    async def download_video(self, video_info: dict[str, Any]) -> bool:
        """Скачивает видео с максимальной скоростью"""
        message = video_info["message"]
        filename = self.generate_filename(message)
        file_path = self.output_dir / filename
        
        print(f"\n{self.total_downloaded + 1}. Downloading: {filename}")
        print(f"Size: {self.format_size(video_info['size'])}")
        
        # Показываем текст
        if video_info['text']:
            preview = video_info['text'][:100] + "..." if len(video_info['text']) > 100 else video_info['text']
            print(f"Text: {preview}")
        
        # Дополнительная проверка - если файл уже существует
        if file_path.exists():
            actual_size = file_path.stat().st_size
            print(f"File already exists! Size: {self.format_size(actual_size)}")
            
            # Добавляем в скачанные и считаем успешным
            self.total_downloaded += 1
            self.total_size += actual_size
            self.downloaded_ids.add(message.id)
            
            return True
        
        self._download_start = time.time()
        
        try:
            # Используем уже авторизованный клиент но с оптимизациями
            from src.mcp_telegram.telegram import create_client
            
            client = create_client()
            await client.connect()
            
            # Проверяем текущий DC и оптимизируем
            try:
                dc_id = client.session.dc_id
                print(f"Connected to DC {dc_id}")
            except:
                pass
            
            # РАДИКАЛЬНЫЕ настройки для максимальной скорости
            client.flood_sleep_threshold = 0
            if hasattr(client, '_flood_sleep_threshold'):
                client._flood_sleep_threshold = 0
            
            # Отключаем все виды throttling
            if hasattr(client, '_request_retries'):
                client._request_retries = 10
            if hasattr(client, '_connection_retries'):
                client._connection_retries = 10
            if hasattr(client, '_retry_delay'):
                client._retry_delay = 0.1
            
            # Настройки MTProto для скорости
            if hasattr(client, '_sender') and client._sender:
                client._sender.flood_sleep_threshold = 0
                if hasattr(client._sender, '_flood_sleep_threshold'):
                    client._sender._flood_sleep_threshold = 0
                
                # Дополнительные настройки sender'а
                if hasattr(client._sender, '_retries'):
                    client._sender._retries = 10
                if hasattr(client._sender, '_delay'):
                    client._sender._delay = 0.1
                
                # Пытаемся оптимизировать connection
                if hasattr(client._sender, '_connection'):
                    conn = client._sender._connection
                    if hasattr(conn, 'recv_buffer_size'):
                        conn.recv_buffer_size = 1024 * 1024  # 1MB буфер
                    if hasattr(conn, 'send_buffer_size'):
                        conn.send_buffer_size = 1024 * 1024  # 1MB буфер
            
            try:
                print("Downloading with maximum speed settings...")
                
                # Скачиваем с оптимизированными настройками
                downloaded_file = await asyncio.wait_for(
                    client.download_media(
                        message.media,
                        file=str(file_path),
                        progress_callback=self.progress_callback
                    ),
                    timeout=3600
                )
                
                download_time = time.time() - self._download_start
                actual_size = file_path.stat().st_size if file_path.exists() else 0
                speed = actual_size / download_time if download_time > 0 else 0
                
                print(f"\nSUCCESS! Time: {self.format_time(download_time)}")
                print(f"Speed: {self.format_size(speed)}/s")
                print(f"Size: {self.format_size(actual_size)}")
                
                # Обновляем статистику
                self.total_downloaded += 1
                self.total_size += actual_size
                self.downloaded_ids.add(message.id)
                
                # Сохраняем результат
                result = {
                    "success": True,
                    "message_id": message.id,
                    "filename": filename,
                    "file_path": str(file_path),
                    "size": actual_size,
                    "download_time": download_time,
                    "speed": speed,
                    "text": video_info["text"],
                    "media_type": video_info["media_type"],
                    "download_timestamp": datetime.now().isoformat(),
                }
                self.save_result(result)
                
                return True
                
            finally:
                await client.disconnect()
                    
        except Exception as e:
            download_time = time.time() - self._download_start
            print(f"\nFAILED: {e}")
            print(f"Time: {self.format_time(download_time)}")
            
            # Сохраняем ошибку
            result = {
                "success": False,
                "message_id": message.id,
                "filename": filename,
                "error": str(e),
                "download_time": download_time,
                "text": video_info["text"],
                "media_type": video_info["media_type"],
                "download_timestamp": datetime.now().isoformat(),
            }
            self.save_result(result)
            
            return False

    def show_stats(self):
        """Показывает статистику"""
        elapsed = time.time() - self.start_time
        avg_speed = self.total_size / elapsed if elapsed > 0 else 0
        
        print(f"\nSTATS:")
        print(f"  Downloaded: {self.total_downloaded} files")
        print(f"  Total size: {self.format_size(self.total_size)}")
        print(f"  Time: {self.format_time(elapsed)}")
        print(f"  Average speed: {self.format_size(avg_speed)}/s")

    async def start_download(self, max_files: int = 10):
        """Запускает скачивание"""
        print("PERFECT VIDEO DOWNLOADER")
        print("Features:")
        print("- One file at a time with optimized progress bar")
        print("- Shows real-time download speed and ETA")
        print("- Skips already downloaded files (checks folder)")
        print("- Filters out angular/vue content")
        print("- Auto-continues to next file")
        print("- OPTIMIZED FOR SPEED (no flood limits)")
        print("=" * 50)
        
        downloaded_count = 0
        
        while downloaded_count < max_files:
            print(f"\nSearching for next video...")
            
            # Ищем следующее видео
            video_info = await self.find_next_video()
            
            if not video_info:
                print("No more videos found!")
                break
            
            # Скачиваем видео
            success = await self.download_video(video_info)
            
            if success:
                downloaded_count += 1
                self.show_stats()
                
                # Короткая пауза перед следующим
                await asyncio.sleep(0.5)
            else:
                print("Skipping to next video...")
                await asyncio.sleep(1)
        
        # Финальная статистика
        print(f"\nDOWNLOAD COMPLETED!")
        print(f"Successfully downloaded: {downloaded_count} files")
        self.show_stats()
        print(f"Files saved to: {self.output_dir.absolute()}")


async def main():
    """Основная функция"""
    print("PERFECT MEDIA DOWNLOADER")
    print("Auto-downloading ALL available videos & audio (no limit)...")
    print("Press Ctrl+C to stop at any time")
    print()
    
    # Автоматически скачиваем ВСЕ доступные видео
    max_files = 999999  # Без лимита - качаем все что найдем
    
    downloader = PerfectDownloader()
    
    try:
        await downloader.start_download(max_files)
    except KeyboardInterrupt:
        print("\nDownload stopped by user")
        downloader.show_stats()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())