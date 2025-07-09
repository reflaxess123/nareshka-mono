"""
Железобетонные MCP инструменты с защитой от блокировок
"""

import logging
import typing as t
from functools import singledispatch
from mcp.types import TextContent, ImageContent, EmbeddedResource
from pydantic import BaseModel, ConfigDict

from .robust_client import get_robust_client

logger = logging.getLogger(__name__)

class RobustToolArgs(BaseModel):
    """Базовый класс для аргументов устойчивых инструментов"""
    model_config = ConfigDict()

@singledispatch
async def robust_tool_runner(
    args,  # noqa: ANN001
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Диспетчер для выполнения устойчивых инструментов"""
    raise NotImplementedError(f"No handler for {type(args)}")

# === УСТОЙЧИВЫЕ ИНСТРУМЕНТЫ ===

class RobustListDialogs(RobustToolArgs):
    """Список диалогов через устойчивый клиент"""
    unread: bool = False
    archived: bool = False
    ignore_pinned: bool = False

@robust_tool_runner.register
async def robust_list_dialogs(
    args: RobustListDialogs,
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Получает список диалогов через устойчивый клиент"""
    logger.info(f"RobustListDialogs: {args}")
    
    response: list[TextContent] = []
    
    async with get_robust_client() as client:
        try:
            dialogs = await client.get_dialogs(
                archived=args.archived,
                ignore_pinned=args.ignore_pinned
            )
            
            for dialog in dialogs:
                # Фильтруем по непрочитанным если нужно
                if args.unread and dialog.unread_count == 0:
                    continue
                    
                msg = (
                    f"name='{dialog.name}' id={dialog.id} "
                    f"unread={dialog.unread_count} mentions={dialog.unread_mentions_count}"
                )
                response.append(TextContent(type="text", text=msg))
                
        except Exception as e:
            error_msg = f"Error getting dialogs: {str(e)}"
            logger.error(error_msg)
            response.append(TextContent(type="text", text=error_msg))
    
    return response

class RobustListMessages(RobustToolArgs):
    """Список сообщений через устойчивый клиент"""
    dialog_id: int
    unread: bool = False
    limit: int = 100

@robust_tool_runner.register
async def robust_list_messages(
    args: RobustListMessages,
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Получает сообщения через устойчивый клиент"""
    logger.info(f"RobustListMessages: {args}")
    
    response: list[TextContent] = []
    
    async with get_robust_client() as client:
        try:
            messages = await client.get_messages(
                dialog_id=args.dialog_id,
                limit=args.limit,
                unread=args.unread
            )
            
            for message in messages:
                if hasattr(message, 'text') and message.text:
                    response.append(TextContent(type="text", text=message.text))
                    
        except Exception as e:
            error_msg = f"Error getting messages: {str(e)}"
            logger.error(error_msg)
            response.append(TextContent(type="text", text=error_msg))
    
    return response

class RobustListForumTopics(RobustToolArgs):
    """Список тем форума через устойчивый клиент"""
    dialog_id: int
    limit: int = 100

@robust_tool_runner.register
async def robust_list_forum_topics(
    args: RobustListForumTopics,
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Получает темы форума через устойчивый клиент"""
    logger.info(f"RobustListForumTopics: {args}")
    
    response: list[TextContent] = []
    
    async with get_robust_client() as client:
        try:
            result = await client.get_forum_topics(
                dialog_id=args.dialog_id,
                limit=args.limit
            )
            
            if hasattr(result, 'topics'):
                for topic in result.topics:
                    if hasattr(topic, 'title') and hasattr(topic, 'id'):
                        msg = (
                            f"topic_id={topic.id} title='{topic.title}' "
                            f"unread={getattr(topic, 'unread_count', 0)} "
                            f"top_message={getattr(topic, 'top_message', 0)}"
                        )
                        response.append(TextContent(type="text", text=msg))
            else:
                response.append(TextContent(type="text", text="No topics found or not a forum supergroup"))
                
        except Exception as e:
            error_msg = f"Error getting forum topics: {str(e)}"
            logger.error(error_msg)
            response.append(TextContent(type="text", text=error_msg))
    
    return response

class RobustListTopicMessages(RobustToolArgs):
    """Список сообщений из темы через устойчивый клиент"""
    dialog_id: int
    topic_id: int
    limit: int = 100
    unread: bool = False

@robust_tool_runner.register
async def robust_list_topic_messages(
    args: RobustListTopicMessages,
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Получает сообщения из темы через устойчивый клиент"""
    logger.info(f"RobustListTopicMessages: {args}")
    
    response: list[TextContent] = []
    
    async with get_robust_client() as client:
        try:
            messages = await client.get_topic_messages(
                dialog_id=args.dialog_id,
                topic_id=args.topic_id,
                limit=args.limit
            )
            
            for message in messages:
                if hasattr(message, 'text') and message.text:
                    msg_info = (
                        f"id={message.id} date={message.date} "
                        f"from_id={getattr(message.sender, 'id', 'unknown')} "
                        f"text='{message.text[:200]}{'...' if len(message.text) > 200 else ''}'"
                    )
                    response.append(TextContent(type="text", text=msg_info))
                    
            if not response:
                response.append(TextContent(type="text", text=f"No messages found in topic {args.topic_id}"))
                
        except Exception as e:
            error_msg = f"Error getting topic messages: {str(e)}"
            logger.error(error_msg)
            response.append(TextContent(type="text", text=error_msg))
    
    return response

class RobustFindTopicByName(RobustToolArgs):
    """Поиск темы по имени через устойчивый клиент"""
    dialog_id: int
    topic_name: str

@robust_tool_runner.register
async def robust_find_topic_by_name(
    args: RobustFindTopicByName,
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Ищет тему по имени через устойчивый клиент"""
    logger.info(f"RobustFindTopicByName: {args}")
    
    response: list[TextContent] = []
    
    async with get_robust_client() as client:
        try:
            topic = await client.find_topic_by_name(
                dialog_id=args.dialog_id,
                topic_name=args.topic_name
            )
            
            if topic:
                msg = (
                    f"FOUND: topic_id={topic.id} title='{topic.title}' "
                    f"unread={getattr(topic, 'unread_count', 0)} "
                    f"top_message={getattr(topic, 'top_message', 0)}"
                )
                response.append(TextContent(type="text", text=msg))
            else:
                response.append(TextContent(type="text", text=f"Topic '{args.topic_name}' not found"))
                
        except Exception as e:
            error_msg = f"Error finding topic: {str(e)}"
            logger.error(error_msg)
            response.append(TextContent(type="text", text=error_msg))
    
    return response

# === ИНТЕГРАЦИЯ С СУЩЕСТВУЮЩЕЙ СИСТЕМОЙ ===

def get_robust_tool_description(tool_class):
    """Получает описание устойчивого инструмента"""
    from mcp.types import Tool
    
    return Tool(
        name=tool_class.__name__,
        description=tool_class.__doc__ or f"Robust version of {tool_class.__name__}",
        inputSchema=tool_class.model_json_schema()
    )

def get_robust_tool_args(tool_name: str, **kwargs) -> RobustToolArgs:
    """Создает аргументы для устойчивого инструмента"""
    tool_classes = {
        'RobustListDialogs': RobustListDialogs,
        'RobustListMessages': RobustListMessages,
        'RobustListForumTopics': RobustListForumTopics,
        'RobustListTopicMessages': RobustListTopicMessages,
        'RobustFindTopicByName': RobustFindTopicByName,
    }
    
    # Добавляем медиа инструменты если доступны
    try:
        from .media_tools import RobustDownloadVideo, RobustFindVideos, RobustScanMedia
        tool_classes.update({
            'RobustDownloadVideo': RobustDownloadVideo,
            'RobustFindVideos': RobustFindVideos,
            'RobustScanMedia': RobustScanMedia,
        })
    except ImportError:
        pass
    
    if tool_name not in tool_classes:
        raise ValueError(f"Unknown robust tool: {tool_name}")
    
    return tool_classes[tool_name](**kwargs)

# === СПИСОК ВСЕХ УСТОЙЧИВЫХ ИНСТРУМЕНТОВ ===

ROBUST_TOOLS = [
    RobustListDialogs,
    RobustListMessages,
    RobustListForumTopics,
    RobustListTopicMessages,
    RobustFindTopicByName,
]

# Импортируем медиа инструменты
try:
    from .media_tools import RobustDownloadVideo, RobustFindVideos, RobustScanMedia
    ROBUST_TOOLS.extend([
        RobustDownloadVideo,
        RobustFindVideos,
        RobustScanMedia,
    ])
except ImportError:
    pass  # Медиа инструменты не доступны 