# app/api/__init__.py
from fastapi import APIRouter
from .webhook_router import router as webhook_router

# Создаем общий роутер API
api_router = APIRouter()

# Подключаем наш webhook-роутер
api_router.include_router(webhook_router)