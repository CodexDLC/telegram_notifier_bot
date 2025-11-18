# app/bot/handlers/commands.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger as log

from app.bot.formatter import MessageInfoFormatter

# Создаем роутер для команд
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Приветственное сообщение"""
    await message.answer(
        "👋 <b>Привет! Я GitHub Notifier Bot.</b>\n\n"
        "Я умею пересылать уведомления о Pull Request'ах из GitHub в этот чат.\n"
        "Чтобы узнать ID этого чата для настройки, введите /get_ids"
    )


@router.message(Command("get_ids"))
async def cmd_get_ids(message: Message):
    """Показывает ID чата и топика для настройки .env"""
    log.info(f"User {message.from_user.id} requested IDs in chat {message.chat.id}")

    # Используем ваш форматтер
    text = MessageInfoFormatter.format_chat_ids_only(message)
    await message.answer(text)


@router.message(Command("get_full_info"))
async def cmd_full_info(message: Message):
    """Показывает полную техническую информацию (для отладки)"""
    text = MessageInfoFormatter.format_full_info(message)
    await message.answer(text)