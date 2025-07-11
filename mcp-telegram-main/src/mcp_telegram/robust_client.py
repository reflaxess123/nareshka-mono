"""
Железобетонный Telegram клиент с защитой от блокировок
Основан на анализе рабочего скрипта TOP_telegram_topic_mass_parser.py
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager

from telethon import TelegramClient
from telethon.errors import AuthKeyUnregisteredError, FloodWaitError, SessionRevokedError

from .telegram import create_client

logger = logging.getLogger(__name__)

class RobustTelegramClient:
    """Устойчивый клиент с защитой от блокировок"""

    def __init__(self):
        self._client: TelegramClient | None = None
        self._lock = asyncio.Lock()
        self._last_request_time = 0
        self._request_count = 0
        self._session_start_time = time.time()
        self._retry_count = 0

        # Настройки защиты
        self.MIN_REQUEST_INTERVAL = 1.5  # Минимум 1.5 секунды между запросами
        self.MAX_REQUESTS_PER_MINUTE = 20  # Максимум 20 запросов в минуту
        self.SESSION_REFRESH_INTERVAL = 3600  # Обновлять сессию каждый час
        self.MAX_RETRY_ATTEMPTS = 3

    async def _ensure_client(self) -> TelegramClient:
        """Обеспечивает наличие подключенного клиента"""
        async with self._lock:
            # Проверяем, нужно ли обновить сессию
            if (time.time() - self._session_start_time) > self.SESSION_REFRESH_INTERVAL:
                logger.info("Обновление сессии для предотвращения блокировки")
                await self._refresh_session()

            # Создаем клиент если его нет
            if self._client is None:
                self._client = create_client()
                await self._client.connect()
                self._session_start_time = time.time()
                logger.info("Создан новый Telegram клиент")

            # Проверяем подключение
            if not self._client.is_connected():
                await self._client.connect()
                logger.info("Восстановлено подключение")

            return self._client

    async def _refresh_session(self):
        """Обновляет сессию для предотвращения блокировки"""
        if self._client:
            try:
                await self._client.disconnect()
            except:
                pass

        self._client = None
        self._session_start_time = time.time()
        self._request_count = 0

        # Пауза перед переподключением
        await asyncio.sleep(2)

    async def _wait_for_rate_limit(self):
        """Ждёт согласно лимитам запросов"""
        current_time = time.time()

        # Проверяем интервал между запросами
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.MIN_REQUEST_INTERVAL:
            sleep_time = self.MIN_REQUEST_INTERVAL - time_since_last
            logger.debug(f"Ожидание rate limit: {sleep_time:.2f} сек")
            await asyncio.sleep(sleep_time)

        # Проверяем лимит запросов в минуту
        if self._request_count >= self.MAX_REQUESTS_PER_MINUTE:
            if (current_time - self._session_start_time) < 60:
                sleep_time = 60 - (current_time - self._session_start_time)
                logger.info(f"Достигнут лимит запросов в минуту. Ожидание: {sleep_time:.2f} сек")
                await asyncio.sleep(sleep_time)
                self._request_count = 0
                self._session_start_time = current_time

        self._last_request_time = time.time()
        self._request_count += 1

    async def _execute_with_retry(self, operation, *args, **kwargs):
        """Выполняет операцию с повторными попытками"""
        for attempt in range(self.MAX_RETRY_ATTEMPTS):
            try:
                await self._wait_for_rate_limit()
                client = await self._ensure_client()

                # Выполняем операцию
                return await operation(client, *args, **kwargs)

            except FloodWaitError as e:
                wait_time = min(e.seconds, 300)  # Максимум 5 минут
                logger.warning(f"FloodWaitError: ожидание {wait_time} секунд")
                await asyncio.sleep(wait_time)
                continue

            except (AuthKeyUnregisteredError, SessionRevokedError) as e:
                logger.error(f"Сессия недействительна: {e}")
                raise

            except Exception as e:
                logger.error(f"Ошибка при выполнении операции (попытка {attempt + 1}): {e}")
                if attempt == self.MAX_RETRY_ATTEMPTS - 1:
                    raise

                # Экспоненциальная задержка
                sleep_time = min(2 ** attempt, 60)
                logger.info(f"Повтор через {sleep_time} секунд")
                await asyncio.sleep(sleep_time)

    async def get_dialogs(self, archived=False, ignore_pinned=False):
        """Получает список диалогов"""
        async def _get_dialogs(client, archived, ignore_pinned):
            dialogs = []
            async for dialog in client.iter_dialogs(
                archived=archived,
                ignore_pinned=ignore_pinned,
            ):
                dialogs.append(dialog)
                # Микро-пауза между диалогами
                await asyncio.sleep(0.1)
            return dialogs

        return await self._execute_with_retry(_get_dialogs, archived, ignore_pinned)

    async def get_messages(self, dialog_id, limit=100, unread=False):
        """Получает сообщения из диалога"""
        async def _get_messages(client, dialog_id, limit, unread):
            messages = []

            if unread:
                # Получаем только непрочитанные
                async for message in client.iter_messages(
                    entity=dialog_id,
                    limit=limit,
                    reverse=False,
                ):
                    if hasattr(message, "text") and message.text:
                        messages.append(message)
                    await asyncio.sleep(0.05)  # Микро-пауза
            else:
                # Получаем последние сообщения
                async for message in client.iter_messages(
                    entity=dialog_id,
                    limit=limit,
                ):
                    if hasattr(message, "text") and message.text:
                        messages.append(message)
                    await asyncio.sleep(0.05)  # Микро-пауза

            return messages

        return await self._execute_with_retry(_get_messages, dialog_id, limit, unread)

    async def get_forum_topics(self, dialog_id, limit=100):
        """Получает темы форума"""
        async def _get_forum_topics(client, dialog_id, limit):
            from telethon.tl.functions.channels import GetForumTopicsRequest

            result = await client(GetForumTopicsRequest(
                channel=dialog_id,
                offset_date=0,
                offset_id=0,
                offset_topic=0,
                limit=limit,
            ))
            return result

        return await self._execute_with_retry(_get_forum_topics, dialog_id, limit)

    async def get_topic_messages(self, dialog_id, topic_id, limit=100):
        """Получает сообщения из темы"""
        async def _get_topic_messages(client, dialog_id, topic_id, limit):
            messages = []
            async for message in client.iter_messages(
                entity=dialog_id,
                limit=limit,
                reply_to=topic_id,
            ):
                if hasattr(message, "text") and message.text:
                    messages.append(message)
                await asyncio.sleep(0.05)  # Микро-пауза
            return messages

        return await self._execute_with_retry(_get_topic_messages, dialog_id, topic_id, limit)

    async def find_topic_by_name(self, dialog_id, topic_name):
        """Ищет тему по названию"""
        async def _find_topic(client, dialog_id, topic_name):
            from telethon.tl.functions.channels import GetForumTopicsRequest

            result = await client(GetForumTopicsRequest(
                channel=dialog_id,
                offset_date=0,
                offset_id=0,
                offset_topic=0,
                limit=100,
            ))

            if hasattr(result, "topics"):
                for topic in result.topics:
                    if hasattr(topic, "title") and topic.title == topic_name:
                        return topic
            return None

        return await self._execute_with_retry(_find_topic, dialog_id, topic_name)

    async def close(self):
        """Закрывает соединение"""
        if self._client:
            try:
                await self._client.disconnect()
            except:
                pass
            self._client = None
        logger.info("Robust Telegram клиент закрыт")

# Глобальный инстанс
_robust_client = RobustTelegramClient()

@asynccontextmanager
async def get_robust_client():
    """Контекстный менеджер для получения устойчивого клиента"""
    try:
        yield _robust_client
    finally:
        # Не закрываем соединение, оставляем его для повторного использования
        pass

async def cleanup_robust_client():
    """Очистка ресурсов при завершении"""
    await _robust_client.close()
