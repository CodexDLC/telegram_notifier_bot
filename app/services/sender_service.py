# app/services/sender_service.py
from aiogram.exceptions import TelegramAPIError
from loguru import logger as log

from app.bot.loader import bot
from app.core.config import (
    NOTIFY_CHANNEL_ID,
    PR_TOPIC_ID,
    PUSH_TOPIC_ID,
    ISSUES_TOPIC_ID,
    CICD_TOPIC_ID,
    RELEASES_TOPIC_ID,
    SECURITY_TOPIC_ID,
)


async def send_pr_notification(text: str) -> bool:
    """
    Отправляет уведомление о Pull Request в топик PR.

    :param text: Текст сообщения (HTML)
    :return: True, если успешно, иначе False
    """
    return await _send_to_channel(text, PR_TOPIC_ID, "Pull Request")


async def send_push_notification(text: str) -> bool:
    """
    Отправляет уведомление о Push в топик Push.

    :param text: Текст сообщения (HTML)
    :return: True, если успешно, иначе False
    """
    return await _send_to_channel(text, PUSH_TOPIC_ID, "Push")


async def _send_to_channel(text: str, topic_id: int | None, event_type: str) -> bool:
    """
    Внутренняя функция для отправки сообщения в канал/топик.

    :param text: Текст сообщения (HTML)
    :param topic_id: ID топика (может быть None)
    :param event_type: Тип события (для логов)
    :return: True, если успешно, иначе False
    """
    if not NOTIFY_CHANNEL_ID:
        log.warning(f"[{event_type}] NOTIFY_CHANNEL_ID не задан. Сообщение не отправлено.")
        return False

    try:
        await bot.send_message(
            chat_id=NOTIFY_CHANNEL_ID,
            message_thread_id=topic_id,  # Если None, отправит в общий чат
            text=text,
            disable_web_page_preview=True
        )

        topic_info = f":{topic_id}" if topic_id else " (общий чат)"
        log.info(f"✅ [{event_type}] Уведомление отправлено в {NOTIFY_CHANNEL_ID}{topic_info}")
        return True

    except TelegramAPIError as e:
        log.error(f"❌ [{event_type}] Ошибка при отправке в Telegram: {e}")
        return False