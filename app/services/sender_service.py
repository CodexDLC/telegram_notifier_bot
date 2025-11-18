# app/services/sender_service.py
from aiogram.exceptions import TelegramAPIError
from loguru import logger as log

from app.bot.loader import bot
from app.core.config import PR_NOTIFY_CHANNEL_ID, PR_NOTIFY_TOPIC_ID


async def send_to_channel(text: str) -> bool:
    """
    Отправляет сообщение в настроенный канал (и топик, если есть).

    :param text: Текст сообщения (HTML)
    :return: True, если успешно, иначе False
    """
    if not PR_NOTIFY_CHANNEL_ID:
        log.warning("Не задан PR_NOTIFY_CHANNEL_ID. Сообщение не отправлено.")
        return False

    try:
        await bot.send_message(
            chat_id=PR_NOTIFY_CHANNEL_ID,
            message_thread_id=PR_NOTIFY_TOPIC_ID,  # Если None, отправит в общий чат
            text=text,
            disable_web_page_preview=True  # Чтобы не было огромных превью ссылок GitHub
        )
        log.info(f"Уведомление успешно отправлено в чат {PR_NOTIFY_CHANNEL_ID}:{PR_NOTIFY_TOPIC_ID}")
        return True

    except TelegramAPIError as e:
        log.error(f"Ошибка при отправке в Telegram: {e}")
        return False