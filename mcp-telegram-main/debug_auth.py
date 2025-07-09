import asyncio
import logging
from src.mcp_telegram.telegram import create_client

# Включаем отладочные логи
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_auth():
    client = create_client()
    
    try:
        print("Connecting to Telegram...")
        await client.connect()
        print(f"Connected: {client.is_connected()}")
        
        print("Checking authorization...")
        is_authorized = await client.is_user_authorized()
        print(f"Is authorized: {is_authorized}")
        
        if is_authorized:
            print("Getting user info...")
            user = await client.get_me()
            print(f"User: {user}")
        else:
            print("User not authorized")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_auth()) 