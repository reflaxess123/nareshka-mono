"""
Тест скачивания видео из Telegram
"""

import asyncio
from src.mcp_telegram.simple_video_downloader import simple_scan_media, simple_download_media, simple_find_and_download

async def test_scan_media():
    """Тест сканирования медиа файлов"""
    print("🔍 Сканирование медиа файлов в диалоге 'ОМ: Паровозик собеседований'...")
    
    dialog_id = -1002208833410
    media_list = await simple_scan_media(dialog_id, limit=50)
    
    if media_list and not media_list[0].get("error"):
        print(f"📂 Найдено {len(media_list)} медиа файлов:")
        for i, media in enumerate(media_list[:10], 1):  # Показываем первые 10
            print(f"  {i}. ID: {media['message_id']} | Тип: {media['media_type']}")
            if media['text']:
                print(f"     Текст: {media['text'][:50]}...")
    else:
        print("❌ Медиа файлы не найдены или ошибка")
    
    return media_list

async def test_download_media():
    """Тест скачивания медиа файлов"""
    print("\n🎬 Поиск и скачивание медиа файлов...")
    
    dialog_id = -1002208833410
    results = await simple_find_and_download(dialog_id, limit=3)
    
    if results and not results[0].get("error"):
        print(f"✅ Скачано {len(results)} файлов:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['file_path']}")
            print(f"     Тип: {result['media_type']}")
            print(f"     Сообщение: {result['message_id']}")
    else:
        print("❌ Ошибка скачивания или медиа не найдены")
    
    return results

async def main():
    """Основная функция теста"""
    print("🚀 Запуск теста скачивания видео из Telegram\n")
    
    # Сканируем медиа файлы
    media_list = await test_scan_media()
    
    # Скачиваем медиа файлы
    if media_list and not media_list[0].get("error"):
        await test_download_media()
    
    print("\n🏁 Тест завершен!")

if __name__ == "__main__":
    asyncio.run(main()) 