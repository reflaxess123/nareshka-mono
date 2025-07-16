"""
АНАЛИЗАТОР МЕДИА ФАЙЛОВ В ЧАТЕ
Подсчитывает все видео/аудио файлы, их размер и время скачивания
"""

import asyncio
import time
from pathlib import Path
from datetime import datetime


class MediaAnalyzer:
    """Анализирует все медиа файлы в Telegram чате"""

    def __init__(self):
        self.dialog_id = -1002208833410
        self.topic_id = 31
        
        # Фильтр для пропуска angular/vue
        self.skip_keywords = [
            'angular', 'vue', 'vuejs', 'vue.js', 'nuxt', 
            'angular2', 'angular4', 'angular5', 'angular6', 'angular7', 
            'angular8', 'angular9', 'angular10', 'angular11', 'angular12',
            'angular13', 'angular14', 'angular15', 'angular16', 'angular17',
            'ng-', 'ngrx', 'angular cli', 'angular material'
        ]
        
        # Статистика
        self.total_videos = 0
        self.total_audio = 0
        self.total_video_size = 0
        self.total_audio_size = 0
        self.total_other_media = 0
        self.total_other_size = 0
        self.skipped_angular = 0
        
        self.media_files = []
        self.monthly_stats = {}  # Статистика по месяцам
        self.company_stats = {}  # Статистика по компаниям
        
        self.start_time = None

    def extract_company_from_text(self, text: str) -> str:
        """Извлекает название компании из текста"""
        if not text:
            return "Unknown"
        
        text_lower = text.lower()
        
        # Известные компании
        companies = {
            'яндекс': 'Яндекс', 'yandex': 'Яндекс',
            'сбер': 'Сбербанк', 'sber': 'Сбербанк', 'сбербанк': 'Сбербанк',
            'авито': 'Авито', 'avito': 'Авито',
            'вк': 'VK', 'vk': 'VK', 'вконтакте': 'VK',
            'тинькофф': 'Тинькофф', 'tinkoff': 'Тинькофф',
            'ozon': 'Ozon', 'озон': 'Ozon',
            'wildberries': 'Wildberries', 'вайлдберриз': 'Wildberries',
            'альфа': 'Альфа-Банк', 'alfa': 'Альфа-Банк',
            'мтс': 'МТС', 'mts': 'МТС',
            'ростелеком': 'Ростелеком',
            'циан': 'Циан', 'cian': 'Циан',
            'rutube': 'RuTube', 'рутуб': 'RuTube',
            'exness': 'Exness',
            'точка': 'Точка Банк', 'точкабанк': 'Точка Банк',
            'selecty': 'Selecty',
            'иннотех': 'Иннотех',
            'смайнекс': 'Sminex', 'sminex': 'Sminex',
            'spotware': 'Spotware',
            'мтг': 'МТГ',
            'рокет': 'Рокет',
            'exness': 'Exness'
        }
        
        for key, company in companies.items():
            if key in text_lower:
                return company
        
        # Попробуем найти через #
        import re
        hashtag_match = re.search(r'#([A-Za-zА-Яа-я]+)', text)
        if hashtag_match:
            tag = hashtag_match.group(1)
            if tag.lower() not in ['frontend', 'react', 'vue', 'angular', 'javascript', 'typescript', 'запись_собеса']:
                return tag
        
        return "Other"

    def should_skip(self, text: str) -> bool:
        """Проверяет нужно ли пропустить по ключевым словам"""
        if not text:
            return False
        text_lower = text.lower()
        for keyword in self.skip_keywords:
            if keyword in text_lower:
                return True
        return False

    def format_size(self, size_bytes: int) -> str:
        """Форматирует размер"""
        if size_bytes == 0:
            return "0 B"
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def format_time(self, seconds: float) -> str:
        """Форматирует время"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    async def analyze_all_media(self):
        """Анализирует все медиа файлы в чате"""
        print("🔍 АНАЛИЗ ВСЕХ МЕДИА ФАЙЛОВ В ЧАТЕ")
        print("=" * 50)
        print("📡 Подключаемся к Telegram...")
        
        try:
            from src.mcp_telegram.telegram import create_client
            
            client = create_client()
            await client.connect()
            
            print(f"📊 Сканируем сообщения в чате {self.dialog_id}, топик {self.topic_id}...")
            print("⏳ Это может занять несколько минут...")
            print()
            
            message_count = 0
            
            async for message in client.iter_messages(
                entity=self.dialog_id,
                limit=100000,  # Очень большой лимит для всех сообщений
                reply_to=self.topic_id,
                reverse=True,  # С самого начала
            ):
                message_count += 1
                
                # Показываем прогресс каждые 100 сообщений
                if message_count % 100 == 0:
                    print(f"📝 Обработано сообщений: {message_count}")
                
                # Только медиа файлы
                if not message.media:
                    continue
                
                # Проверяем на angular/vue
                text = message.text or ""
                if self.should_skip(text):
                    self.skipped_angular += 1
                    continue
                
                # Анализируем медиа
                media_info = {
                    "message_id": message.id,
                    "date": message.date,
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "media_type": str(type(message.media).__name__)
                }
                
                # Статистика по месяцам
                if message.date:
                    month_key = message.date.strftime('%Y-%m')
                    if month_key not in self.monthly_stats:
                        self.monthly_stats[month_key] = {'videos': 0, 'audio': 0, 'size': 0}
                
                # Извлекаем компанию из текста
                company = self.extract_company_from_text(text)
                
                # Получаем размер и тип
                size = 0
                file_type = "unknown"
                
                if hasattr(message.media, "document") and message.media.document:
                    size = getattr(message.media.document, "size", 0)
                    mime_type = getattr(message.media.document, "mime_type", "").lower()
                    
                    if mime_type.startswith('video/'):
                        file_type = "video"
                        self.total_videos += 1
                        self.total_video_size += size
                        if message.date:
                            month_key = message.date.strftime('%Y-%m')
                            self.monthly_stats[month_key]['videos'] += 1
                            self.monthly_stats[month_key]['size'] += size
                    elif mime_type.startswith('audio/'):
                        file_type = "audio"
                        self.total_audio += 1
                        self.total_audio_size += size
                        if message.date:
                            month_key = message.date.strftime('%Y-%m')
                            self.monthly_stats[month_key]['audio'] += 1
                            self.monthly_stats[month_key]['size'] += size
                    elif 'video' in mime_type:
                        file_type = "video"
                        self.total_videos += 1
                        self.total_video_size += size
                        if message.date:
                            month_key = message.date.strftime('%Y-%m')
                            self.monthly_stats[month_key]['videos'] += 1
                            self.monthly_stats[month_key]['size'] += size
                    elif 'audio' in mime_type:
                        file_type = "audio"
                        self.total_audio += 1
                        self.total_audio_size += size
                        if message.date:
                            month_key = message.date.strftime('%Y-%m')
                            self.monthly_stats[month_key]['audio'] += 1
                            self.monthly_stats[month_key]['size'] += size
                    else:
                        file_type = "other"
                        self.total_other_media += 1
                        self.total_other_size += size
                    
                    # Статистика по компаниям
                    if company and file_type in ['video', 'audio']:
                        if company not in self.company_stats:
                            self.company_stats[company] = {'count': 0, 'size': 0}
                        self.company_stats[company]['count'] += 1
                        self.company_stats[company]['size'] += size
                else:
                    # Возможно это фото или другой тип медиа
                    file_type = "other"
                    self.total_other_media += 1
                
                media_info.update({
                    "size": size,
                    "file_type": file_type,
                    "mime_type": getattr(getattr(message.media, "document", None), "mime_type", "unknown"),
                    "company": company
                })
                
                self.media_files.append(media_info)
            
            await client.disconnect()
            
            print(f"\n✅ Обработано всего сообщений: {message_count}")
            print(f"📊 Найдено медиа файлов: {len(self.media_files)}")
            print(f"🎬 Видео: {self.total_videos}, 🎵 Аудио: {self.total_audio}")
            print("\n🎉 Анализ завершен!")
            
        except Exception as e:
            print(f"❌ Ошибка при анализе: {e}")

    def show_statistics(self):
        """Показывает детальную статистику"""
        output = []
        
        output.append("# 📊 СТАТИСТИКА МЕДИА ФАЙЛОВ В ЧАТЕ")
        output.append("")
        
        output.append("## 🎬 ВИДЕО ФАЙЛЫ")
        output.append(f"- **Количество:** {self.total_videos}")
        output.append(f"- **Общий размер:** {self.format_size(self.total_video_size)}")
        output.append("")
        
        output.append("## 🎵 АУДИО ФАЙЛЫ")
        output.append(f"- **Количество:** {self.total_audio}")
        output.append(f"- **Общий размер:** {self.format_size(self.total_audio_size)}")
        output.append("")
        
        output.append("## 📄 ДРУГИЕ МЕДИА")
        output.append(f"- **Количество:** {self.total_other_media}")
        output.append(f"- **Общий размер:** {self.format_size(self.total_other_size)}")
        output.append("")
        
        output.append(f"## 🚫 ПРОПУЩЕНО (Angular/Vue)")
        output.append(f"- **Количество:** {self.skipped_angular}")
        output.append("")
        
        # Общая статистика
        total_media = self.total_videos + self.total_audio
        total_size = self.total_video_size + self.total_audio_size
        
        output.append("## 📈 ИТОГО (видео + аудио)")
        output.append(f"- **Файлов:** {total_media}")
        output.append(f"- **Размер:** {self.format_size(total_size)}")
        output.append("")
        
        # Расчет времени скачивания
        output.append("## ⏱️ ОЦЕНКА ВРЕМЕНИ СКАЧИВАНИЯ")
        output.append("")
        
        # При текущей медленной скорости 200-250 KB/s
        slow_speed_200 = 200 * 1024  # 200 KB/s в байтах
        slow_speed_250 = 250 * 1024  # 250 KB/s в байтах
        time_200 = total_size / slow_speed_200 if slow_speed_200 > 0 else 0
        time_250 = total_size / slow_speed_250 if slow_speed_250 > 0 else 0
        
        # При нормальной скорости 1 MB/s
        normal_speed = 1024 * 1024  # 1 MB/s
        time_normal = total_size / normal_speed
        
        # При быстрой скорости 5 MB/s (как у официального Telegram)
        fast_speed = 5 * 1024 * 1024  # 5 MB/s
        time_fast = total_size / fast_speed
        
        output.append("| Скорость | Время скачивания |")
        output.append("|----------|------------------|")
        output.append(f"| **200 KB/s** (текущая) | **{self.format_time(time_200)}** |")
        output.append(f"| **250 KB/s** (текущая) | **{self.format_time(time_250)}** |")
        output.append(f"| 1 MB/s (нормальная) | {self.format_time(time_normal)} |")
        output.append(f"| 5 MB/s (быстрая) | {self.format_time(time_fast)} |")
        output.append("")
        
        # Средний размер файла
        if total_media > 0:
            avg_size = total_size / total_media
            output.append("## 📊 СРЕДНИЙ РАЗМЕР ФАЙЛА")
            output.append(f"- **Размер:** {self.format_size(avg_size)}")
            output.append("")
        
        # Выводим в консоль
        for line in output:
            print(line)
        
        return output

    def show_largest_files(self, count=10):
        """Показывает самые большие файлы"""
        output = []
        
        output.append(f"## 🔝 ТОП {count} САМЫХ БОЛЬШИХ ФАЙЛОВ")
        output.append("")
        
        # Фильтруем только видео и аудио
        media_only = [f for f in self.media_files if f['file_type'] in ['video', 'audio']]
        
        # Сортируем по размеру
        largest = sorted(media_only, key=lambda x: x['size'], reverse=True)[:count]
        
        output.append("| № | Размер | Тип | ID | Компания | Описание |")
        output.append("|---|--------|-----|----|---------|---------| ")
        
        for i, file in enumerate(largest, 1):
            company = file.get('company', 'Unknown')
            text_preview = file['text'][:40] + "..." if len(file['text']) > 40 else file['text']
            text_preview = text_preview.replace("|", "\\|").replace("\n", " ")  # Экранируем символы таблицы
            
            output.append(f"| {i} | {self.format_size(file['size'])} | {file['file_type']} | {file['message_id']} | {company} | {text_preview} |")
        
        output.append("")
        
        # Выводим в консоль
        for line in output:
            print(line)
        
        return output

    def save_report(self):
        """Сохраняет отчет в MD файл"""
        report_lines = []
        
        # Основная статистика
        total_media = self.total_videos + self.total_audio
        total_size = self.total_video_size + self.total_audio_size
        
        # При текущей медленной скорости 200-250 KB/s
        slow_speed_200 = 200 * 1024
        time_200 = total_size / slow_speed_200 if slow_speed_200 > 0 else 0
        
        report_lines.append(f"# АНАЛИЗ МЕДИА ФАЙЛОВ")
        report_lines.append(f"")
        report_lines.append(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**Всего файлов:** {total_media} (видео: {self.total_videos}, аудио: {self.total_audio})")
        report_lines.append(f"**Общий размер:** {self.format_size(total_size)}")
        report_lines.append(f"**Время скачки (200 KB/s):** {self.format_time(time_200)}")
        report_lines.append("")
        
        # ВСЕ ЗАПИСИ В ТАБЛИЦЕ
        report_lines.append("## ПОЛНЫЙ СПИСОК ФАЙЛОВ")
        report_lines.append("")
        
        # Фильтруем только видео и аудио, сортируем по размеру
        media_only = [f for f in self.media_files if f['file_type'] in ['video', 'audio']]
        sorted_media = sorted(media_only, key=lambda x: x['size'], reverse=True)
        
        report_lines.append("| № | ID | Тип | Размер | Компания | Дата | Описание |")
        report_lines.append("|---|----|----|--------|----------|------|----------|")
        
        for i, file in enumerate(sorted_media, 1):
            company = file.get('company', 'Unknown')
            date_str = file['date'].strftime('%Y-%m-%d') if file['date'] else 'Unknown'
            text_preview = file['text'][:60] + "..." if len(file['text']) > 60 else file['text']
            text_preview = text_preview.replace("|", "\\|").replace("\n", " ").strip()
            
            report_lines.append(f"| {i} | {file['message_id']} | {file['file_type']} | {self.format_size(file['size'])} | {company} | {date_str} | {text_preview} |")
        
        report_lines.append("")
        
        # Сохраняем файл
        filename = f"media_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = Path(filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"\n💾 Отчет сохранен: {filepath.absolute()}")
        return filepath


async def main():
    """Основная функция"""
    analyzer = MediaAnalyzer()
    analyzer.start_time = time.time()
    
    try:
        await analyzer.analyze_all_media()
        analyzer.show_statistics()
        analyzer.show_largest_files(15)
        
        # Сохраняем отчет
        report_path = analyzer.save_report()
        
        elapsed = time.time() - analyzer.start_time
        print(f"\n⏱️ Время анализа: {analyzer.format_time(elapsed)}")
        
    except KeyboardInterrupt:
        print("\nАнализ прерван пользователем")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())