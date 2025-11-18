# app/bot/loader.py
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.config import BOT_TOKEN

# Создаем экземпляр бота с HTML-парсингом по умолчанию
# (чтобы можно было писать жирным шрифтом <b>...</b>)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Диспетчер для обработки входящих команд (например /get_ids)
dp = Dispatcher()