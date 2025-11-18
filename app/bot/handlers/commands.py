# app/bot/handlers/commands.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger as log

from app.bot.formatter import MessageInfoFormatter

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Приветственное сообщение"""
    await message.answer(
        "👋 <b>Привет! Я GitHub Notifier Bot.</b>\n\n"
        "Я умею пересылать уведомления из GitHub в Telegram:\n"
        "• 🟢 <b>Pull Requests</b> → в отдельный топик\n"
        "• 📦 <b>Push события</b> → в отдельный топик\n\n"
        "Чтобы узнать ID этого чата для настройки, введите /get_ids"
    )


@router.message(Command("get_ids"))
async def cmd_get_ids(message: Message):
    """Показывает ID чата и топика для настройки .env"""
    log.info(f"User {message.from_user.id} requested IDs in chat {message.chat.id}")

    text = "🆔 <b>ID для настройки (.env):</b>\n\n"
    text += f"NOTIFY_CHANNEL_ID=<code>{message.chat.id}</code>\n"

    if message.message_thread_id:
        text += f"\n<b>Этот топик:</b>\n"
        text += f"ID топика: <code>{message.message_thread_id}</code>\n\n"
        text += "<i>💡 Создайте два топика в своей группе:</i>\n"
        text += "1️⃣ Топик <b>Pull Requests</b>\n"
        text += "2️⃣ Топик <b>Pushes</b>\n\n"
        text += "Затем отправьте /get_ids в каждом из них, чтобы узнать их ID."
    else:
        text += "\n<i>💡 Совет: Создайте топики в супергруппе для раздельных уведомлений</i>"

    text += "\n\n<i>(Нажмите на число, чтобы скопировать)</i>"
    await message.answer(text)


@router.message(Command("get_full_info"))
async def cmd_full_info(message: Message):
    """Показывает полную техническую информацию (для отладки)"""
    text = MessageInfoFormatter.format_full_info(message)
    await message.answer(text)