import os

from xdg_base_dirs import xdg_state_home

from src.mcp_telegram.telegram import TelegramSettings, create_client

# Проверяем путь к сессии
state_home = xdg_state_home() / "mcp-telegram"
session_file = state_home / "mcp_telegram_session.session"

print(f"XDG State Home: {xdg_state_home()}")
print(f"Session directory: {state_home}")
print(f"Session file path: {session_file}")
print(f"Directory exists: {os.path.exists(state_home)}")
print(f"Session file exists: {os.path.exists(session_file)}")

if os.path.exists(state_home):
    print(f"Directory contents: {list(state_home.iterdir())}")
    if os.path.exists(session_file):
        stat = os.stat(session_file)
        print(f"Session file size: {stat.st_size} bytes")
        print(f"Session file modified: {stat.st_mtime}")

# Проверяем настройки
try:
    config = TelegramSettings()
    print(f"API ID: {config.api_id}")
    print(f"API Hash: {config.api_hash[:10]}...")
except Exception as e:
    print(f"Config error: {e}")

# Проверяем создание клиента
try:
    client = create_client()
    print(f"Client created: {client}")
    print(f"Client session: {client.session}")
except Exception as e:
    print(f"Client creation error: {e}")
