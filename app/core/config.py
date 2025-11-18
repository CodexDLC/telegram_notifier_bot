# app/core/config.py
import os
import sys
from dotenv import load_dotenv
from loguru import logger as log

# Загружаем переменные из .env
load_dotenv()

# --- Telegram Bot ---
BOT_TOKEN: str | None = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    log.critical("BOT_TOKEN не найден в .env! Бот не может быть запущен.")
    # Принудительно останавливаем, если нет токена
    sys.exit(1)

# --- Channel / Topic ---
PR_NOTIFY_CHANNEL_ID_STR: str | None = os.getenv("PR_NOTIFY_CHANNEL_ID")
PR_NOTIFY_TOPIC_ID_STR: str | None = os.getenv("PR_NOTIFY_TOPIC_ID")

# Преобразуем ID в числа (int), если они заданы
try:
    PR_NOTIFY_CHANNEL_ID: int | None = int(PR_NOTIFY_CHANNEL_ID_STR) if PR_NOTIFY_CHANNEL_ID_STR else None
    PR_NOTIFY_TOPIC_ID: int | None = int(PR_NOTIFY_TOPIC_ID_STR) if PR_NOTIFY_TOPIC_ID_STR else None
except ValueError:
    log.error("ID канала или топика должны быть числами!")
    PR_NOTIFY_CHANNEL_ID = None
    PR_NOTIFY_TOPIC_ID = None

# --- Webhook Secret (Для будущего) ---
GITHUB_WEBHOOK_SECRET: str | None = os.getenv("GITHUB_WEBHOOK_SECRET")