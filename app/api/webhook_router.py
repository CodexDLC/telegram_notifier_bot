# app/api/webhook_router.py
from fastapi import APIRouter, Request
from loguru import logger as log

from app.services.webhook_service import process_github_payload

router = APIRouter()

@router.post("/webhook/github")
async def github_webhook_endpoint(request: Request):
    """
    Основной эндпоинт, принимающий события от GitHub.
    URL: http://ВАШ_IP/webhook/github
    """
    client_host = request.client.host if request.client else "unknown"
    log.info(f"📥 Входящий Webhook от {client_host}")

    # Передаем запрос в сервис.
    # Он сам проверит подпись, распарсит JSON и отправит сообщение боту.
    result = await process_github_payload(request)

    return result