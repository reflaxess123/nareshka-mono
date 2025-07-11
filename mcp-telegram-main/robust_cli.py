"""
CLI для тестирования железобетонных Telegram инструментов
"""

import asyncio
import json
import logging
from functools import wraps

import typer
from rich.console import Console
from rich.json import JSON
from rich.table import Table

from src.mcp_telegram.robust_server import call_tool, list_tools

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = typer.Typer(help="Robust Telegram MCP CLI")
console = Console()

def typer_async(f):
    """Декоратор для асинхронных функций typer"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

@app.command()
@typer_async
async def list_robust_tools() -> None:
    """Показать список устойчивых инструментов"""

    console.print("🛡️  [bold green]Robust Telegram MCP Tools[/bold green]")
    console.print()

    try:
        tools = await list_tools()

        # Создаем таблицу
        table = Table(title="Устойчивые инструменты")
        table.add_column("Название", style="cyan")
        table.add_column("Описание", style="magenta")
        table.add_column("Параметры", style="green")

        for tool in tools:
            schema_json = json.dumps(tool.inputSchema.get("properties", {}), indent=2)
            table.add_row(
                tool.name,
                tool.description or "Нет описания",
                JSON(schema_json),
            )

        console.print(table)
        console.print(f"\n✅ Найдено {len(tools)} устойчивых инструментов")

    except Exception as e:
        console.print(f"❌ Ошибка: {e}")

@app.command()
@typer_async
async def call_robust_tool(
    name: str = typer.Argument(help="Название инструмента"),
    args: str = typer.Option("{}", help="Аргументы в формате JSON"),
) -> None:
    """Вызвать устойчивый инструмент"""

    console.print(f"🔧 Вызов инструмента: [bold]{name}[/bold]")
    console.print(f"📋 Аргументы: {args}")
    console.print()

    try:
        # Парсим аргументы
        arguments = json.loads(args)

        # Вызываем инструмент
        console.print("⏳ Выполняется запрос...")
        result = await call_tool(name, arguments)

        console.print("✅ Результат:")
        console.print("─" * 50)

        for item in result:
            if item.type == "text":
                console.print(item.text)
            else:
                console.print(f"[yellow]Тип: {item.type}[/yellow]")
                console.print(str(item))

        console.print("─" * 50)
        console.print(f"📊 Получено {len(result)} элементов")

    except json.JSONDecodeError:
        console.print("❌ Ошибка: Некорректный JSON в аргументах")
    except Exception as e:
        console.print(f"❌ Ошибка: {e}")

@app.command()
@typer_async
async def test_dialogs() -> None:
    """Тестирование получения списка диалогов"""

    console.print("📱 Тестирование получения диалогов...")

    try:
        result = await call_tool("RobustListDialogs", {})

        console.print("✅ Диалоги:")
        for item in result:
            if item.type == "text":
                console.print(f"  • {item.text}")

        console.print(f"\n📊 Найдено {len(result)} диалогов")

    except Exception as e:
        console.print(f"❌ Ошибка: {e}")

@app.command()
@typer_async
async def test_messages(
    dialog_id: int = typer.Argument(help="ID диалога"),
    limit: int = typer.Option(10, help="Количество сообщений"),
) -> None:
    """Тестирование получения сообщений"""

    console.print(f"💬 Тестирование получения сообщений из {dialog_id}...")

    try:
        result = await call_tool("RobustListMessages", {
            "dialog_id": dialog_id,
            "limit": limit,
        })

        console.print("✅ Сообщения:")
        for item in result:
            if item.type == "text":
                console.print(f"  • {item.text[:100]}{'...' if len(item.text) > 100 else ''}")

        console.print(f"\n📊 Получено {len(result)} сообщений")

    except Exception as e:
        console.print(f"❌ Ошибка: {e}")

@app.command()
@typer_async
async def test_forum_topics(
    dialog_id: int = typer.Argument(help="ID диалога"),
    limit: int = typer.Option(10, help="Количество тем"),
) -> None:
    """Тестирование получения тем форума"""

    console.print(f"🗂️  Тестирование получения тем форума из {dialog_id}...")

    try:
        result = await call_tool("RobustListForumTopics", {
            "dialog_id": dialog_id,
            "limit": limit,
        })

        console.print("✅ Темы форума:")
        for item in result:
            if item.type == "text":
                console.print(f"  • {item.text}")

        console.print(f"\n📊 Найдено {len(result)} тем")

    except Exception as e:
        console.print(f"❌ Ошибка: {e}")

@app.command()
@typer_async
async def test_topic_messages(
    dialog_id: int = typer.Argument(help="ID диалога"),
    topic_id: int = typer.Argument(help="ID темы"),
    limit: int = typer.Option(10, help="Количество сообщений"),
) -> None:
    """Тестирование получения сообщений из темы"""

    console.print(f"🧵 Тестирование получения сообщений из темы {topic_id}...")

    try:
        result = await call_tool("RobustListTopicMessages", {
            "dialog_id": dialog_id,
            "topic_id": topic_id,
            "limit": limit,
        })

        console.print("✅ Сообщения темы:")
        for item in result:
            if item.type == "text":
                console.print(f"  • {item.text[:100]}{'...' if len(item.text) > 100 else ''}")

        console.print(f"\n📊 Получено {len(result)} сообщений")

    except Exception as e:
        console.print(f"❌ Ошибка: {e}")

@app.command()
@typer_async
async def find_topic(
    dialog_id: int = typer.Argument(help="ID диалога"),
    topic_name: str = typer.Argument(help="Название темы"),
) -> None:
    """Тестирование поиска темы по названию"""

    console.print(f"🔍 Поиск темы '{topic_name}' в диалоге {dialog_id}...")

    try:
        result = await call_tool("RobustFindTopicByName", {
            "dialog_id": dialog_id,
            "topic_name": topic_name,
        })

        console.print("✅ Результат поиска:")
        for item in result:
            if item.type == "text":
                console.print(f"  • {item.text}")

    except Exception as e:
        console.print(f"❌ Ошибка: {e}")

# === НОВЫЕ КОМАНДЫ ДЛЯ ВИДЕО ===

@app.command()
@typer_async
async def scan_media(
    dialog_id: int = typer.Argument(help="ID диалога"),
    limit: int = typer.Option(20, help="Количество сообщений для сканирования"),
) -> None:
    """Сканирование медиа файлов в диалоге"""

    console.print(f"📂 Сканирование медиа файлов в диалоге {dialog_id}...")

    try:
        result = await call_tool("RobustScanMedia", {
            "dialog_id": dialog_id,
            "limit": limit,
        })

        console.print("✅ Результат сканирования:")
        for item in result:
            if item.type == "text":
                console.print(item.text)

    except Exception as e:
        console.print(f"❌ Ошибка: {e}")

@app.command()
@typer_async
async def download_video(
    dialog_id: int = typer.Argument(help="ID диалога"),
    message_id: int = typer.Argument(help="ID сообщения"),
    path: str = typer.Option(None, help="Путь для сохранения"),
) -> None:
    """Скачивание видео из сообщения"""

    console.print(f"🎬 Скачивание видео из сообщения {message_id}...")

    try:
        args = {
            "dialog_id": dialog_id,
            "message_id": message_id,
        }
        if path:
            args["custom_path"] = path

        result = await call_tool("RobustDownloadVideo", args)

        console.print("✅ Результат:")
        for item in result:
            if item.type == "text":
                console.print(item.text)

    except Exception as e:
        console.print(f"❌ Ошибка: {e}")

@app.command()
@typer_async
async def find_videos(
    dialog_id: int = typer.Argument(help="ID диалога"),
    limit: int = typer.Option(5, help="Количество видео для поиска"),
    min_duration: int = typer.Option(0, help="Минимальная длительность (сек)"),
) -> None:
    """Поиск и скачивание видео в диалоге"""

    console.print(f"🔍 Поиск видео в диалоге {dialog_id}...")

    try:
        result = await call_tool("RobustFindVideos", {
            "dialog_id": dialog_id,
            "limit": limit,
            "min_duration": min_duration,
        })

        console.print("✅ Результат поиска:")
        for item in result:
            if item.type == "text":
                console.print(item.text)

    except Exception as e:
        console.print(f"❌ Ошибка: {e}")

@app.command()
@typer_async
async def stress_test(
    iterations: int = typer.Option(10, help="Количество итераций"),
    delay: float = typer.Option(2.0, help="Задержка между запросами (сек)"),
) -> None:
    """Стресс-тест устойчивости системы"""

    console.print(f"🧪 Стресс-тест: {iterations} итераций с задержкой {delay}с")
    console.print()

    success_count = 0
    error_count = 0

    for i in range(iterations):
        try:
            console.print(f"🔄 Итерация {i + 1}/{iterations}")

            # Тестируем получение диалогов
            result = await call_tool("RobustListDialogs", {})

            if result and len(result) > 0:
                success_count += 1
                console.print(f"  ✅ Успешно: {len(result)} диалогов")
            else:
                error_count += 1
                console.print("  ❌ Пустой результат")

            # Пауза между запросами
            if i < iterations - 1:
                await asyncio.sleep(delay)

        except Exception as e:
            error_count += 1
            console.print(f"  ❌ Ошибка: {e}")

    console.print()
    console.print("📊 Результаты стресс-теста:")
    console.print(f"  ✅ Успешно: {success_count}")
    console.print(f"  ❌ Ошибок: {error_count}")
    console.print(f"  📈 Успешность: {(success_count / iterations) * 100:.1f}%")

if __name__ == "__main__":
    app()
