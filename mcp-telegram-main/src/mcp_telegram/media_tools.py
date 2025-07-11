"""
MCP инструменты для работы с медиа файлами
"""

import logging
import typing as t

from mcp.types import EmbeddedResource, ImageContent, TextContent

from .media_downloader import download_video_from_message, find_videos_in_dialog, scan_dialog_media
from .robust_tools import RobustToolArgs, robust_tool_runner

logger = logging.getLogger(__name__)

# === МЕДИА ИНСТРУМЕНТЫ ===

class RobustDownloadVideo(RobustToolArgs):
    """Скачивание видео из конкретного сообщения"""
    dialog_id: int
    message_id: int
    custom_path: str = None

@robust_tool_runner.register
async def robust_download_video(
    args: RobustDownloadVideo,
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Скачивает видео из сообщения"""
    logger.info(f"RobustDownloadVideo: {args}")

    response: list[TextContent] = []

    try:
        result = await download_video_from_message(
            args.dialog_id,
            args.message_id,
            args.custom_path,
        )

        if result.get("success"):
            media_info = result["media_info"]
            file_path = result["file_path"]

            info_text = (
                f"✅ ВИДЕО СКАЧАНО:\n"
                f"📁 Файл: {file_path}\n"
                f"📊 Размер: {media_info['size']} байт\n"
                f"⏱️ Длительность: {media_info['duration']} сек\n"
                f"📐 Разрешение: {media_info['width']}x{media_info['height']}\n"
                f"💬 Сообщение: {args.message_id}\n"
                f"🗨️ Диалог: {args.dialog_id}"
            )
            response.append(TextContent(type="text", text=info_text))
        else:
            error_text = f"❌ Ошибка скачивания: {result.get('error', 'Неизвестная ошибка')}"
            response.append(TextContent(type="text", text=error_text))

    except Exception as e:
        error_msg = f"❌ Ошибка: {e!s}"
        logger.error(error_msg)
        response.append(TextContent(type="text", text=error_msg))

    return response

class RobustFindVideos(RobustToolArgs):
    """Поиск и скачивание видео в диалоге"""
    dialog_id: int
    limit: int = 5
    min_duration: int = 0

@robust_tool_runner.register
async def robust_find_videos(
    args: RobustFindVideos,
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Находит и скачивает видео из диалога"""
    logger.info(f"RobustFindVideos: {args}")

    response: list[TextContent] = []

    try:
        results = await find_videos_in_dialog(
            args.dialog_id,
            args.limit,
            args.min_duration,
        )

        if not results:
            response.append(TextContent(type="text", text="❌ Видео не найдено"))
            return response

        response.append(TextContent(type="text", text=f"🎬 НАЙДЕНО И СКАЧАНО {len(results)} ВИДЕО:"))

        for i, result in enumerate(results, 1):
            if result.get("success"):
                media_info = result["media_info"]
                file_path = result["file_path"]

                video_text = (
                    f"\n📹 Видео {i}:\n"
                    f"📁 {file_path}\n"
                    f"📊 {media_info['size']} байт\n"
                    f"⏱️ {media_info['duration']} сек\n"
                    f"📐 {media_info['width']}x{media_info['height']}\n"
                    f"💬 ID: {result['message_id']}"
                )
                response.append(TextContent(type="text", text=video_text))
            else:
                error_text = f"❌ Ошибка скачивания {i}: {result.get('error')}"
                response.append(TextContent(type="text", text=error_text))

    except Exception as e:
        error_msg = f"❌ Ошибка поиска видео: {e!s}"
        logger.error(error_msg)
        response.append(TextContent(type="text", text=error_msg))

    return response

class RobustScanMedia(RobustToolArgs):
    """Сканирование медиа файлов в диалоге"""
    dialog_id: int
    limit: int = 20

@robust_tool_runner.register
async def robust_scan_media(
    args: RobustScanMedia,
) -> t.Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Сканирует медиа файлы в диалоге"""
    logger.info(f"RobustScanMedia: {args}")

    response: list[TextContent] = []

    try:
        media_list = await scan_dialog_media(args.dialog_id, args.limit)

        if not media_list:
            response.append(TextContent(type="text", text="❌ Медиа файлы не найдены"))
            return response

        # Группируем по типам
        media_types = {}
        for media in media_list:
            if media.get("error"):
                continue

            media_type = media["media_info"]["type"]
            if media_type not in media_types:
                media_types[media_type] = []
            media_types[media_type].append(media)

        response.append(TextContent(type="text", text=f"📂 НАЙДЕНО {len(media_list)} МЕДИА ФАЙЛОВ:"))

        for media_type, files in media_types.items():
            type_emoji = {
                "video": "🎬",
                "photo": "🖼️",
                "audio": "🎵",
                "document": "📄",
            }

            emoji = type_emoji.get(media_type, "📁")
            response.append(TextContent(type="text", text=f"\n{emoji} {media_type.upper()}: {len(files)} файлов"))

            for media in files[:5]:  # Показываем первые 5
                media_info = media["media_info"]
                size_mb = media_info["size"] / (1024 * 1024) if media_info["size"] else 0

                details = f"📊 {size_mb:.1f} MB"
                if media_info["duration"]:
                    details += f" ⏱️ {media_info['duration']}с"
                if media_info["width"] and media_info["height"]:
                    details += f" 📐 {media_info['width']}x{media_info['height']}"

                media_text = (
                    f"  💬 ID: {media['message_id']} | {details}\n"
                    f"  💭 {media['text'][:50]}{'...' if len(media['text']) > 50 else ''}"
                )
                response.append(TextContent(type="text", text=media_text))

    except Exception as e:
        error_msg = f"❌ Ошибка сканирования медиа: {e!s}"
        logger.error(error_msg)
        response.append(TextContent(type="text", text=error_msg))

    return response

# === ОБНОВЛЯЕМ СПИСОК ИНСТРУМЕНТОВ ===
# Импортируем после определения всех инструментов
try:
    from .robust_tools import ROBUST_TOOLS
    ROBUST_TOOLS.extend([
        RobustDownloadVideo,
        RobustFindVideos,
        RobustScanMedia,
    ])
except ImportError:
    pass  # Основные инструменты не доступны
