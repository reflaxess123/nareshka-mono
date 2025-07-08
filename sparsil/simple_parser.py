#!/usr/bin/env python3
"""
Простой парсер ВСЕХ сообщений из чата Frontend – TO THE JOB
"""

import json
import time

# Функция для вызова MCP API
def get_messages(offset=None):
    """Получает сообщения через MCP API"""
    # Здесь должен быть вызов MCP, но пока имитируем
    print(f"Получаем сообщения с offset: {offset}")
    return {"messages": [], "offset": None}  # Заглушка

def parse_all_messages():
    """Парсит ВСЕ сообщения из чата"""
    all_messages = []
    offset = None
    page = 1
    
    print("🚀 Начинаем парсинг ВСЕХ сообщений из чата...")
    
    while True:
        print(f"📄 Страница {page}, offset: {offset}")
        
        # Получаем сообщения (здесь нужно заменить на реальный MCP вызов)
        response = get_messages(offset)
        
        if not response or "messages" not in response:
            print("❌ Нет ответа от API")
            break
            
        messages = response["messages"]
        
        if not messages:
            print("✅ Достигнут конец чата")
            break
            
        all_messages.extend(messages)
        print(f"📥 Получено {len(messages)} сообщений. Всего: {len(all_messages)}")
        
        # Получаем новый offset
        if "offset" in response:
            offset = response["offset"]
        else:
            break
            
        page += 1
        time.sleep(0.5)  # Пауза между запросами
    
    print(f"🎉 ГОТОВО! Собрано {len(all_messages)} сообщений")
    
    # Сохраняем все сообщения
    with open("all_chat_messages.json", "w", encoding="utf-8") as f:
        json.dump(all_messages, f, ensure_ascii=False, indent=2)
    
    print("💾 Все сообщения сохранены в all_chat_messages.json")
    return all_messages

def main():
    print("📱 Простой парсер чата Frontend – TO THE JOB")
    print("="*50)
    
    # ИНСТРУКЦИЯ ДЛЯ ПОЛЬЗОВАТЕЛЯ:
    print("\n🔧 ЧТО НУЖНО СДЕЛАТЬ:")
    print("1. Замените функцию get_messages() на реальный вызов MCP")
    print("2. Используйте эти команды для получения данных:")
    print()
    print("   # Первый запрос:")
    print("   mcp_telegram_tg_dialog(name='chn[2071074234:9204039393350586818]')")
    print()
    print("   # Следующие запросы с offset:")
    print("   mcp_telegram_tg_dialog(name='chn[2071074234:9204039393350586818]', offset=OFFSET)")
    print()
    print("3. Скопируйте все результаты в один файл")
    print("4. Запустите анализ")
    
    # Пока что запускаем с заглушкой
    messages = parse_all_messages()

if __name__ == "__main__":
    main() 