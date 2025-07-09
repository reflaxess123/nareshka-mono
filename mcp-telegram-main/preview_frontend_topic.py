"""
Предварительный анализ топика Frontend
Показывает статистику сообщений и медиа файлов
"""

import asyncio
from datetime import datetime
from collections import defaultdict

from src.mcp_telegram.robust_client import get_robust_client

class FrontendTopicAnalyzer:
    """Анализатор топика Frontend"""
    
    def __init__(self):
        self.dialog_id = -1002208833410  # ОМ: паравозик собеседований
        self.topic_id = 31  # Frontend топик
    
    async def analyze_topic(self, limit: int = 500):
        """Анализирует топик Frontend"""
        print("🔍 АНАЛИЗ ТОПИКА FRONTEND")
        print("=" * 50)
        
        messages = []
        media_stats = defaultdict(int)
        users_stats = defaultdict(int)
        dates_stats = defaultdict(int)
        
        async with get_robust_client() as client:
            try:
                print(f"📥 Получение {limit} сообщений из топика...")
                
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
                        await asyncio.sleep(0.05)  # Микро-пауза
                    return messages
                
                messages = await client._execute_with_retry(_get_topic_messages, self.dialog_id, self.topic_id, limit)
                
                print(f"✅ Получено {len(messages)} сообщений")
                
                # Собираем статистику
                for message in messages:
                    # Статистика по медиа
                    if message.media:
                        media_type = str(type(message.media).__name__)
                        media_stats[media_type] += 1
                    else:
                        media_stats["Без медиа"] += 1
                    
                    # Статистика по пользователям
                    if message.sender:
                        if hasattr(message.sender, 'username') and message.sender.username:
                            users_stats[f"@{message.sender.username}"] += 1
                        elif hasattr(message.sender, 'first_name') and message.sender.first_name:
                            users_stats[message.sender.first_name] += 1
                        else:
                            users_stats[f"ID:{message.sender.id}"] += 1
                    
                    # Статистика по датам
                    if message.date:
                        date_str = message.date.strftime("%Y-%m")
                        dates_stats[date_str] += 1
                
                # Показываем статистику
                self.show_statistics(messages, media_stats, users_stats, dates_stats)
                
                # Показываем примеры сообщений с медиа
                self.show_media_examples(messages)
                
            except Exception as e:
                print(f"❌ Ошибка анализа: {e}")
    
    def show_statistics(self, messages, media_stats, users_stats, dates_stats):
        """Показывает статистику"""
        print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"  📝 Всего сообщений: {len(messages)}")
        
        if messages:
            oldest = min(msg.date for msg in messages if msg.date)
            newest = max(msg.date for msg in messages if msg.date)
            print(f"  📅 Период: {oldest.strftime('%Y-%m-%d')} - {newest.strftime('%Y-%m-%d')}")
        
        print(f"\n🎬 СТАТИСТИКА ПО МЕДИА:")
        for media_type, count in sorted(media_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(messages) * 100) if messages else 0
            print(f"  {media_type}: {count} ({percentage:.1f}%)")
        
        print(f"\n👥 ТОП-10 АКТИВНЫХ ПОЛЬЗОВАТЕЛЕЙ:")
        for user, count in sorted(users_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {user}: {count} сообщений")
        
        print(f"\n📅 АКТИВНОСТЬ ПО МЕСЯЦАМ:")
        for date, count in sorted(dates_stats.items(), reverse=True)[:12]:
            print(f"  {date}: {count} сообщений")
    
    def show_media_examples(self, messages):
        """Показывает примеры сообщений с медиа"""
        print(f"\n🎬 ПРИМЕРЫ СООБЩЕНИЙ С МЕДИА:")
        
        media_messages = [msg for msg in messages if msg.media][:10]
        
        for i, message in enumerate(media_messages, 1):
            media_type = str(type(message.media).__name__)
            date_str = message.date.strftime("%Y-%m-%d %H:%M") if message.date else "Неизвестно"
            
            print(f"\n  {i}. ID: {message.id} | Дата: {date_str}")
            print(f"     Тип медиа: {media_type}")
            
            if message.text:
                preview = message.text[:150] + "..." if len(message.text) > 150 else message.text
                print(f"     Текст: {preview}")
            
            if message.sender:
                sender_name = ""
                if hasattr(message.sender, 'username') and message.sender.username:
                    sender_name = f"@{message.sender.username}"
                elif hasattr(message.sender, 'first_name') and message.sender.first_name:
                    sender_name = message.sender.first_name
                else:
                    sender_name = f"ID:{message.sender.id}"
                print(f"     Автор: {sender_name}")

async def main():
    """Основная функция"""
    analyzer = FrontendTopicAnalyzer()
    
    # Спрашиваем лимит сообщений
    try:
        limit = int(input("Введите лимит сообщений для анализа (по умолчанию 200): ") or "200")
    except ValueError:
        limit = 200
    
    await analyzer.analyze_topic(limit)
    
    print(f"\n💡 Используйте frontend_video_downloader.py для скачивания видео")

if __name__ == "__main__":
    asyncio.run(main()) 