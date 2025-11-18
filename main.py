# main.py
import asyncio
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger as log

from app.bot.handlers import bot_router
from app.core.logger import setup_logger
from app.bot.loader import bot, dp

# --- ИМПОРТИРУЕМ НАШ НОВЫЙ API РОУТЕР ---
from app.api import api_router  # <--- ДОБАВИТЬ ЭТО

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    log.info("🚀 Запуск приложения...")

    dp.include_router(bot_router)

    polling_task = asyncio.create_task(dp.start_polling(bot))
    log.info("🤖 Бот запущен (polling mode)")

    yield

    log.info("🛑 Остановка приложения...")
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass

    await bot.session.close()
    log.info("🤖 Сессия бота закрыта")

app = FastAPI(title="Telegram GitHub Notifier", lifespan=lifespan)

# --- ПОДКЛЮЧАЕМ РОУТЕР В ПРИЛОЖЕНИЕ ---
app.include_router(api_router)  # <--- ДОБАВИТЬ ЭТО

@app.get("/")
async def root():
    return {"status": "ok", "service": "Telegram GitHub Notifier"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)