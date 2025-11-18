# app/core/logger.py
import logging
import sys
from loguru import logger

class InterceptHandler(logging.Handler):
    """Перехватывает логи стандартной библиотеки logging и отправляет их в Loguru."""
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logger():
    """Настройка логгера при старте приложения."""
    # Удаляем стандартный обработчик, чтобы не было дублей
    logger.remove()

    # Вывод в консоль (Красивый цветной лог)
    logger.add(
        sys.stdout,
        level="DEBUG",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # Перехват логов от библиотек (aiogram, uvicorn)
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING) # Чтобы uvicorn не спамил запросами
    logging.getLogger("aiogram").setLevel(logging.INFO)

    logger.info("Логгер успешно настроен.")