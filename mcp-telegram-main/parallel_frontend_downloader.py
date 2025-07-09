"""
ПАРАЛЛЕЛЬНОЕ СКАЧИВАНИЕ ВИДЕО ИЗ ТОПИКА FRONTEND
С прогрессом, показом размеров и оптимизацией скорости
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import time
from concurrent.futures import ThreadPoolExecutor

from src.mcp_telegram.simple_video_downloader import simple_download_media
from src.mcp_telegram.robust_client import get_robust_client

class ParallelFrontendDownloader:
    """Параллельный загрузчик видео из топика Frontend"""
    
    def __init__(self, max_parallel: int = 3):
        self.dialog_id = -1002208833410  # ОМ: паравозик собеседований
        self.topic_id = 31  # Frontend топик
        self.max_parallel = max_parallel  # Максимум параллельных загрузок
        self.output_dir = Path("./frontend_videos_parallel")
        self.output_dir.mkdir(exist_ok=True)
        
        # Файлы для отслеживания
        self.metadata_file = self.output_dir / "posts_and_videos.json"
        self.progress_file = self.output_dir / "download_progress.json"
        
        # Статистика
        self.total_downloaded = 0
        self.total_size = 0
        self.start_time = None
        self.posts_data = []
        
        # Семафор для ограничения параллельных загрузок
        self.download_semaphore = asyncio.Semaphore(max_parallel)
    
    async def get_messages_with_media_info(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Получает сообщения с информацией о медиа файлах"""
        print(f"📥 Получение сообщений из топика Frontend (лимит: {limit})...")
        
        async with get_robust_client() as client:
            try:
                async def _get_topic_messages(telethon_client, dialog_id, topic_id, limit):
                    messages = []
                    async for message in telethon_client.iter_messages(
                        entity=dialog_id,
                        limit=limit,
                        reply_to=topic_id,
                        reverse=False
                    ):
                        # Собираем информацию о сообщении
                        message_info = {
                            'message': message,
                            'id': message.id,
                            'date': message.date,
                            'text': message.text or "",
                            'has_media': bool(message.media),
                            'media_type': str(type(message.media).__name__) if message.media else None,
                            'estimated_size': 0
                        }
                        
                        # Получаем размер медиа файла
                        if message.media and hasattr(message.media, 'document'):
                            if hasattr(message.media.document, 'size'):
                                message_info['estimated_size'] = message.media.document.size
                        
                        messages.append(message_info)
                        await asyncio.sleep(0.05)
                    
                    return messages
                
                messages = await client._execute_with_retry(_get_topic_messages, self.dialog_id, self.topic_id, limit)
                
                # Фильтруем только сообщения с медиа
                media_messages = [msg for msg in messages if msg['has_media']]
                
                total_size = sum(msg['estimated_size'] for msg in media_messages)
                
                print(f"✅ Получено {len(messages)} сообщений")
                print(f"🎬 С медиа файлами: {len(media_messages)}")
                print(f"📊 Общий размер: {self.format_size(total_size)}")
                
                return media_messages
                
            except Exception as e:
                print(f"❌ Ошибка получения сообщений: {e}")
                return []
    
    def format_size(self, size_bytes: int) -> str:
        """Форматирует размер в человекочитаемом виде"""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def format_time(self, seconds: float) -> str:
        """Форматирует время"""
        if seconds < 60:
            return f"{seconds:.1f}с"
        elif seconds < 3600:
            return f"{int(seconds // 60)}м {int(seconds % 60)}с"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}ч {minutes}м"
    
    def generate_filename(self, message_info: Dict[str, Any], index: int) -> str:
        """Генерирует имя файла для видео"""
        message = message_info['message']
        timestamp = message.date.strftime("%Y%m%d_%H%M%S") if message.date else "unknown"
        return f"frontend_{index:04d}_{timestamp}_{message.id}.mp4"
    
    async def download_single_video(self, message_info: Dict[str, Any], index: int, total: int) -> Dict[str, Any]:
        """Скачивает одно видео"""
        async with self.download_semaphore:
            message = message_info['message']
            filename = self.generate_filename(message_info, index)
            file_path = self.output_dir / filename
            
            download_start = time.time()
            
            try:
                print(f"🎬 [{index}/{total}] Скачиваю: {filename}")
                print(f"   📄 Текст: {message_info['text'][:100]}...")
                print(f"   📊 Размер: {self.format_size(message_info['estimated_size'])}")
                
                # Скачиваем медиа
                result = await simple_download_media(
                    self.dialog_id,
                    message.id,
                    str(file_path)
                )
                
                download_time = time.time() - download_start
                
                if result.get("success"):
                    # Получаем реальный размер файла
                    actual_size = file_path.stat().st_size if file_path.exists() else 0
                    speed = actual_size / download_time if download_time > 0 else 0
                    
                    self.total_downloaded += 1
                    self.total_size += actual_size
                    
                    print(f"   ✅ Скачано за {self.format_time(download_time)}")
                    print(f"   🚀 Скорость: {self.format_size(speed)}/с")
                    print(f"   📁 Размер: {self.format_size(actual_size)}")
                    
                    return {
                        'success': True,
                        'filename': filename,
                        'file_path': str(file_path),
                        'size': actual_size,
                        'download_time': download_time,
                        'message_info': message_info
                    }
                else:
                    error_msg = result.get("error", "Неизвестная ошибка")
                    print(f"   ❌ Ошибка: {error_msg}")
                    return {
                        'success': False,
                        'error': error_msg,
                        'message_info': message_info
                    }
                
            except Exception as e:
                print(f"   ❌ Исключение: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'message_info': message_info
                }
    
    def save_progress(self, completed: int, total: int, elapsed: float):
        """Сохраняет прогресс скачивания"""
        progress_data = {
            'completed': completed,
            'total': total,
            'percentage': (completed / total * 100) if total > 0 else 0,
            'elapsed_time': elapsed,
            'estimated_remaining': ((total - completed) * elapsed / completed) if completed > 0 else 0,
            'total_downloaded': self.total_downloaded,
            'total_size': self.total_size,
            'average_speed': self.total_size / elapsed if elapsed > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
    
    def save_metadata(self, results: List[Dict[str, Any]]):
        """Сохраняет метаданные всех скачанных файлов"""
        metadata = []
        
        for result in results:
            message_info = result['message_info']
            message = message_info['message']
            
            post_data = {
                'message_id': message.id,
                'date': message.date.isoformat() if message.date else None,
                'text': message_info['text'],
                'sender_id': getattr(message.sender, 'id', None) if message.sender else None,
                'sender_username': getattr(message.sender, 'username', None) if message.sender else None,
                'media_type': message_info['media_type'],
                'estimated_size': message_info['estimated_size'],
                'success': result['success'],
                'filename': result.get('filename'),
                'file_path': result.get('file_path'),
                'actual_size': result.get('size'),
                'download_time': result.get('download_time'),
                'error': result.get('error'),
                'download_timestamp': datetime.now().isoformat()
            }
            
            metadata.append(post_data)
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    async def download_all_videos(self, messages: List[Dict[str, Any]]):
        """Скачивает все видео параллельно"""
        if not messages:
            return []
        
        self.start_time = time.time()
        total = len(messages)
        
        print(f"\n🚀 ПАРАЛЛЕЛЬНОЕ СКАЧИВАНИЕ {total} ВИДЕО (макс. {self.max_parallel} одновременно)")
        print("=" * 70)
        
        # Создаем задачи для параллельного скачивания
        tasks = []
        for index, message_info in enumerate(messages, 1):
            task = asyncio.create_task(
                self.download_single_video(message_info, index, total)
            )
            tasks.append(task)
        
        # Выполняем все задачи
        results = []
        completed = 0
        
        for task in asyncio.as_completed(tasks):
            result = await task
            results.append(result)
            completed += 1
            
            # Показываем прогресс
            elapsed = time.time() - self.start_time
            self.save_progress(completed, total, elapsed)
            
            print(f"\n📊 ПРОГРЕСС: {completed}/{total} ({completed/total*100:.1f}%)")
            print(f"   ⏱️  Время: {self.format_time(elapsed)}")
            print(f"   ✅ Скачано: {self.total_downloaded}")
            print(f"   📊 Размер: {self.format_size(self.total_size)}")
            
            if completed > 0 and elapsed > 0:
                remaining = (total - completed) * elapsed / completed
                print(f"   ⏳ Осталось: ~{self.format_time(remaining)}")
        
        return results
    
    async def start_download(self, limit: int = 1000):
        """Запускает процесс скачивания"""
        print("🚀 ПАРАЛЛЕЛЬНОЕ СКАЧИВАНИЕ ВИДЕО ИЗ ТОПИКА FRONTEND")
        print("=" * 60)
        
        # Получаем сообщения с медиа
        messages = await self.get_messages_with_media_info(limit)
        if not messages:
            print("❌ Нет сообщений с медиа файлами")
            return
        
        # Скачиваем все видео параллельно
        results = await self.download_all_videos(messages)
        
        # Сохраняем метаданные
        self.save_metadata(results)
        
        # Финальная статистика
        total_time = time.time() - self.start_time
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        average_speed = self.total_size / total_time if total_time > 0 else 0
        
        print(f"\n🏁 СКАЧИВАНИЕ ЗАВЕРШЕНО!")
        print(f"   ✅ Успешно: {successful}")
        print(f"   ❌ Ошибок: {failed}")
        print(f"   📊 Общий размер: {self.format_size(self.total_size)}")
        print(f"   ⏱️  Время: {self.format_time(total_time)}")
        print(f"   🚀 Средняя скорость: {self.format_size(average_speed)}/с")
        print(f"   📁 Папка: {self.output_dir.absolute()}")

async def main():
    """Основная функция"""
    print("Выберите количество параллельных загрузок:")
    print("1 - Безопасно (1 файл)")
    print("2 - Умеренно (2 файла)")
    print("3 - Быстро (3 файла) - рекомендуется")
    print("4 - Агрессивно (4 файла)")
    
    try:
        parallel_choice = input("Выбор (по умолчанию 3): ").strip() or "3"
        max_parallel = int(parallel_choice)
        max_parallel = max(1, min(max_parallel, 5))  # Ограничиваем от 1 до 5
    except ValueError:
        max_parallel = 3
    
    try:
        limit = int(input("Лимит сообщений (по умолчанию 100): ") or "100")
    except ValueError:
        limit = 100
    
    downloader = ParallelFrontendDownloader(max_parallel=max_parallel)
    await downloader.start_download(limit)

if __name__ == "__main__":
    asyncio.run(main()) 