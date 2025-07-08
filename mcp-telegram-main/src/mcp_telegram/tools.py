from __future__ import annotations

import logging
import sys
import typing as t
from functools import singledispatch

from mcp.types import (
    EmbeddedResource,
    ImageContent,
    TextContent,
    Tool,
)
from pydantic import BaseModel, ConfigDict
from telethon import TelegramClient, custom, functions, types  # type: ignore[import-untyped]

from .telegram import create_client

logger = logging.getLogger(__name__)


# How to add a new tool:
#
# 1. Create a new class that inherits from ToolArgs
#    ```python
#    class NewTool(ToolArgs):
#        """Description of the new tool."""
#        pass
#    ```
#    Attributes of the class will be used as arguments for the tool.
#    The class docstring will be used as the tool description.
#
# 2. Implement the tool_runner function for the new class
#    ```python
#    @tool_runner.register
#    async def new_tool(args: NewTool) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
#        pass
#    ```
#    The function should return a sequence of TextContent, ImageContent or EmbeddedResource.
#    The function should be async and accept a single argument of the new class.
#
# 3. Done! Restart the client and the new tool should be available.


class ToolArgs(BaseModel):
    model_config = ConfigDict()


@singledispatch
async def tool_runner(
    args,  # noqa: ANN001
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    raise NotImplementedError(f"Unsupported type: {type(args)}")


def tool_description(args: type[ToolArgs]) -> Tool:
    return Tool(
        name=args.__name__,
        description=args.__doc__,
        inputSchema=args.model_json_schema(),
    )


def tool_args(tool: Tool, *args, **kwargs) -> ToolArgs:  # noqa: ANN002, ANN003
    return sys.modules[__name__].__dict__[tool.name](*args, **kwargs)


### ListDialogs ###


class ListDialogs(ToolArgs):
    """List available dialogs, chats and channels."""

    unread: bool = False
    archived: bool = False
    ignore_pinned: bool = False


@tool_runner.register
async def list_dialogs(
    args: ListDialogs,
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    client: TelegramClient
    logger.info("method[ListDialogs] args[%s]", args)

    response: list[TextContent] = []
    async with create_client() as client:
        dialog: custom.dialog.Dialog
        async for dialog in client.iter_dialogs(archived=args.archived, ignore_pinned=args.ignore_pinned):
            if args.unread and dialog.unread_count == 0:
                continue
            msg = (
                f"name='{dialog.name}' id={dialog.id} "
                f"unread={dialog.unread_count} mentions={dialog.unread_mentions_count}"
            )
            response.append(TextContent(type="text", text=msg))

    return response


### ListMessages ###


class ListMessages(ToolArgs):
    """
    List messages in a given dialog, chat or channel. The messages are listed in order from newest to oldest.

    If `unread` is set to `True`, only unread messages will be listed. Once a message is read, it will not be
    listed again.

    If `limit` is set, only the last `limit` messages will be listed. If `unread` is set, the limit will be
    the minimum between the unread messages and the limit.
    """

    dialog_id: int
    unread: bool = False
    limit: int = 100


@tool_runner.register
async def list_messages(
    args: ListMessages,
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    client: TelegramClient
    logger.info("method[ListMessages] args[%s]", args)

    response: list[TextContent] = []
    async with create_client() as client:
        result = await client(functions.messages.GetPeerDialogsRequest(peers=[args.dialog_id]))
        if not result:
            raise ValueError(f"Channel not found: {args.dialog_id}")

        if not isinstance(result, types.messages.PeerDialogs):
            raise TypeError(f"Unexpected result: {type(result)}")

        for dialog in result.dialogs:
            logger.debug("dialog: %s", dialog)
        for message in result.messages:
            logger.debug("message: %s", message)

        iter_messages_args: dict[str, t.Any] = {
            "entity": args.dialog_id,
            "reverse": False,
        }
        if args.unread:
            iter_messages_args["limit"] = min(dialog.unread_count, args.limit)
        else:
            iter_messages_args["limit"] = args.limit

        logger.debug("iter_messages_args: %s", iter_messages_args)
        async for message in client.iter_messages(**iter_messages_args):
            logger.debug("message: %s", type(message))
            if isinstance(message, custom.Message) and message.text:
                logger.debug("message: %s", message.text)
                response.append(TextContent(type="text", text=message.text))

    return response


### ListForumTopics ###


class ListForumTopics(ToolArgs):
    """List forum topics (threads) in a supergroup. Works only with forum-enabled supergroups."""

    dialog_id: int
    limit: int = 100


@tool_runner.register
async def list_forum_topics(
    args: ListForumTopics,
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    client: TelegramClient
    logger.info("method[ListForumTopics] args[%s]", args)

    response: list[TextContent] = []
    async with create_client() as client:
        try:
            # Получаем список тем через GetForumTopicsRequest
            result = await client(functions.channels.GetForumTopicsRequest(
                channel=args.dialog_id,
                offset_date=0,
                offset_id=0,
                offset_topic=0,
                limit=args.limit
            ))
            
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
                response.append(TextContent(type="text", text="No topics found or this is not a forum supergroup"))

        except Exception as e:
            logger.error(f"Error getting forum topics: {e}")
            response.append(TextContent(type="text", text=f"Error: {str(e)}"))

    return response


### ListTopicMessages ###


class ListTopicMessages(ToolArgs):
    """
    List messages from a specific forum topic. The messages are listed in order from newest to oldest.
    
    topic_id should be the message ID of the first message in the topic (the topic creation message).
    """

    dialog_id: int
    topic_id: int
    limit: int = 100
    unread: bool = False


@tool_runner.register
async def list_topic_messages(
    args: ListTopicMessages,
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    client: TelegramClient
    logger.info("method[ListTopicMessages] args[%s]", args)

    response: list[TextContent] = []
    async with create_client() as client:
        try:
            # Получаем сообщения из темы используя reply_to_msg_id
            async for message in client.iter_messages(
                entity=args.dialog_id,
                limit=args.limit,
                reply_to=args.topic_id  # Ключевой параметр для фильтрации по теме
            ):
                if isinstance(message, custom.Message):
                    if message.text:
                        # Добавляем информацию о сообщении
                        msg_info = (
                            f"id={message.id} date={message.date} "
                            f"from_id={getattr(message.sender, 'id', 'unknown')} "
                            f"text='{message.text[:200]}{'...' if len(message.text) > 200 else ''}'"
                        )
                        response.append(TextContent(type="text", text=msg_info))
                        
            if not response:
                response.append(TextContent(type="text", text=f"No messages found in topic {args.topic_id}"))

        except Exception as e:
            logger.error(f"Error getting topic messages: {e}")
            response.append(TextContent(type="text", text=f"Error: {str(e)}"))

    return response


### FindTopicByName ###


class FindTopicByName(ToolArgs):
    """Find a forum topic by its name/title in a supergroup."""

    dialog_id: int
    topic_name: str


@tool_runner.register
async def find_topic_by_name(
    args: FindTopicByName,
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    client: TelegramClient
    logger.info("method[FindTopicByName] args[%s]", args)

    response: list[TextContent] = []
    async with create_client() as client:
        try:
            # Получаем все темы
            result = await client(functions.channels.GetForumTopicsRequest(
                channel=args.dialog_id,
                offset_date=0,
                offset_id=0,
                offset_topic=0,
                limit=100
            ))
            
            found_topics = []
            if hasattr(result, 'topics'):
                for topic in result.topics:
                    if hasattr(topic, 'title') and hasattr(topic, 'id'):
                        # Ищем по названию (регистронезависимо)
                        if args.topic_name.lower() in topic.title.lower():
                            found_topics.append({
                                'id': topic.id,
                                'title': topic.title,
                                'unread_count': getattr(topic, 'unread_count', 0),
                                'top_message': getattr(topic, 'top_message', 0)
                            })
            
            if found_topics:
                for topic in found_topics:
                    msg = (
                        f"FOUND: topic_id={topic['id']} title='{topic['title']}' "
                        f"unread={topic['unread_count']} top_message={topic['top_message']}"
                    )
                    response.append(TextContent(type="text", text=msg))
            else:
                response.append(TextContent(type="text", text=f"Topic with name '{args.topic_name}' not found"))

        except Exception as e:
            logger.error(f"Error finding topic: {e}")
            response.append(TextContent(type="text", text=f"Error: {str(e)}"))

    return response
