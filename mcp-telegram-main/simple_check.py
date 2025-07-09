import sqlite3
import os

session_path = r"C:\Users\refla\.local\state\mcp-telegram\mcp_telegram_session.session"

print("=== ПРОСТАЯ ПРОВЕРКА СЕССИИ ===")
print(f"Путь: {session_path}")
print(f"Существует: {os.path.exists(session_path)}")

if os.path.exists(session_path):
    stat = os.stat(session_path)
    print(f"Размер: {stat.st_size} bytes")
    
    try:
        conn = sqlite3.connect(session_path)
        cursor = conn.cursor()
        
        # Проверяем таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Таблицы: {[t[0] for t in tables]}")
        
        # Проверяем sessions
        cursor.execute("SELECT COUNT(*) FROM sessions")
        count = cursor.fetchone()[0]
        print(f"Количество сессий: {count}")
        
        # Проверяем данные
        if count > 0:
            cursor.execute("SELECT dc_id, server_address, port FROM sessions")
            data = cursor.fetchone()
            print(f"DC ID: {data[0]}")
            print(f"Адрес сервера: {data[1]}")
            print(f"Порт: {data[2]}")
            
            # Проверяем ключ авторизации
            cursor.execute("SELECT auth_key FROM sessions")
            auth_key = cursor.fetchone()[0]
            print(f"Ключ авторизации: {'Есть' if auth_key else 'Нет'}")
            print(f"Длина ключа: {len(auth_key) if auth_key else 0} bytes")
        
        conn.close()
        
    except Exception as e:
        print(f"Ошибка SQLite: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Файл сессии не найден!") 