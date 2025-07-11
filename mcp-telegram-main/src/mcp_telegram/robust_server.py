"""
Железобетонный MCP сервер с защитой от блокировок
"""

import asyncio
import logging
import typing as t

from mcp.server import Server
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool

from .robust_client import cleanup_robust_client
from .robust_tools import ROBUST_TOOLS, get_robust_tool_args, get_robust_tool_description, robust_tool_runner

logger = logging.getLogger(__name__)

# Создаем сервер
app = Server("robust-mcp-telegram")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Возвращает список всех устойчивых инструментов"""
    tools = []

    for tool_class in ROBUST_TOOLS:
        tool_desc = get_robust_tool_description(tool_class)
        tools.append(tool_desc)
        logger.debug(f"Registered robust tool: {tool_class.__name__}")

    logger.info(f"Listed {len(tools)} robust tools")
    return tools

@app.call_tool()
async def call_tool(
    name: str,
    arguments: dict[str, t.Any],
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Выполняет устойчивый инструмент"""

    logger.info(f"Calling robust tool: {name} with args: {arguments}")

    try:
        # Создаем аргументы инструмента
        args = get_robust_tool_args(name, **arguments)

        # Выполняем инструмент
        result = await robust_tool_runner(args)

        logger.info(f"Tool {name} completed successfully")
        return result

    except Exception as e:
        logger.error(f"Error in robust tool {name}: {e}")
        error_msg = f"Error in {name}: {e!s}"
        return [TextContent(type="text", text=error_msg)]

async def run_robust_mcp_server() -> None:
    """Запускает устойчивый MCP сервер"""
    logger.info("Starting robust MCP Telegram server...")

    try:
        async with app.run_server() as server:
            logger.info("Robust MCP server is running")
            await server.wait_for_shutdown()
    except Exception as e:
        logger.error(f"Error running robust server: {e}")
        raise
    finally:
        logger.info("Cleaning up robust client...")
        await cleanup_robust_client()
        logger.info("Robust MCP server stopped")

if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Запускаем сервер
    asyncio.run(run_robust_mcp_server())
