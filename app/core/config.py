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
    sys.exit(1)

# --- Channel ID ---
NOTIFY_CHANNEL_ID_STR: str | None = os.getenv("NOTIFY_CHANNEL_ID")

# --- Topic IDs ---
PR_TOPIC_ID_STR: str | None = os.getenv("PR_TOPIC_ID")
PUSH_TOPIC_ID_STR: str | None = os.getenv("PUSH_TOPIC_ID")
ISSUES_TOPIC_ID_STR: str | None = os.getenv("ISSUES_TOPIC_ID")
CICD_TOPIC_ID_STR: str | None = os.getenv("CICD_TOPIC_ID")
RELEASES_TOPIC_ID_STR: str | None = os.getenv("RELEASES_TOPIC_ID")
SECURITY_TOPIC_ID_STR: str | None = os.getenv("SECURITY_TOPIC_ID")

# Преобразуем в числа
try:
    NOTIFY_CHANNEL_ID: int | None = int(NOTIFY_CHANNEL_ID_STR) if NOTIFY_CHANNEL_ID_STR else None
    PR_TOPIC_ID: int | None = int(PR_TOPIC_ID_STR) if PR_TOPIC_ID_STR else None
    PUSH_TOPIC_ID: int | None = int(PUSH_TOPIC_ID_STR) if PUSH_TOPIC_ID_STR else None
    ISSUES_TOPIC_ID: int | None = int(ISSUES_TOPIC_ID_STR) if ISSUES_TOPIC_ID_STR else None
    CICD_TOPIC_ID: int | None = int(CICD_TOPIC_ID_STR) if CICD_TOPIC_ID_STR else None
    RELEASES_TOPIC_ID: int | None = int(RELEASES_TOPIC_ID_STR) if RELEASES_TOPIC_ID_STR else None
    SECURITY_TOPIC_ID: int | None = int(SECURITY_TOPIC_ID_STR) if SECURITY_TOPIC_ID_STR else None
except ValueError:
    log.error("ID канала или топиков должны быть числами!")
    NOTIFY_CHANNEL_ID = None
    PR_TOPIC_ID = None
    PUSH_TOPIC_ID = None
    ISSUES_TOPIC_ID = None
    CICD_TOPIC_ID = None
    RELEASES_TOPIC_ID = None
    SECURITY_TOPIC_ID = None

# --- Webhook Secret ---
GITHUB_WEBHOOK_SECRET: str | None = os.getenv("GITHUB_WEBHOOK_SECRET")

# Логируем конфигурацию при загрузке
if NOTIFY_CHANNEL_ID:
    log.info(f"📢 Канал для уведомлений: {NOTIFY_CHANNEL_ID}")
    if PR_TOPIC_ID:
        log.info(f"  📌 Pull Requests топик: {PR_TOPIC_ID}")
    if PUSH_TOPIC_ID:
        log.info(f"  📌 Pushes топик: {PUSH_TOPIC_ID}")
else:
    log.warning("⚠️ NOTIFY_CHANNEL_ID не настроен. Уведомления не будут отправляться!")