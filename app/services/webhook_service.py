# app/services/webhook_service.py
from fastapi import Request, HTTPException
from loguru import logger as log
import hashlib
import hmac

from app.core.config import GITHUB_WEBHOOK_SECRET
from app.schemas.github_payload import (
    GitHubPullRequestPayload,
    GitHubPushPayload,
    # Здесь должны быть импортированы все Pydantic схемы
    # Но для нашего случая, только эти две используются в process_github_payload
    # GitHubPullRequestReviewPayload,
    # GitHubIssuesPayload,
    # GitHubCheckRunPayload,
    # GitHubReleasePayload,
)
from app.services.sender_service import (
    send_pr_notification,
    send_push_notification,
    # Здесь должны быть импортированы все sender_service
    # send_issues_notification,
    # send_cicd_notification,
    # send_releases_notification,
)
from app.services.report_service import (
    format_pr_message, # Используем импортированные функции
    format_push_message, # Используем импортированные функции
    # Здесь должны быть импортированы все report_service
    # format_pr_review_message,
    # format_issues_message,
    # format_check_run_message,
    # format_release_message,
)


async def verify_signature(request: Request):
    """Проверка подписи GitHub webhook для безопасности"""
    if not GITHUB_WEBHOOK_SECRET:
        log.warning("⚠️ GITHUB_WEBHOOK_SECRET не задан! Проверка подписи пропущена.")
        return

    signature_header = request.headers.get("X-Hub-Signature-256")
    if not signature_header:
        raise HTTPException(status_code=403, detail="Signature header is missing")

    body = await request.body()
    expected = "sha256=" + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(), body, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(status_code=403, detail="Invalid signature")


async def process_github_payload(request: Request):
    """Основная функция обработки webhook от GitHub"""

    # Проверяем подпись
    await verify_signature(request)

    # Получаем тип события
    event_type = request.headers.get("X-GitHub-Event")
    json_data = await request.json()

    log.info(f"📨 Получен webhook: {event_type}")

    try:
        if event_type == "push":
            payload = GitHubPushPayload(**json_data)
            # !!! ИСПОЛЬЗУЕМ ИМПОРТИРОВАННУЮ ФУНКЦИЮ ИЗ report_service !!!
            message = format_push_message(payload)
            if message:
                await send_push_notification(message)
                return {"status": "ok", "event": "push"}

        elif event_type == "pull_request":
            payload = GitHubPullRequestPayload(**json_data)
            # !!! ИСПОЛЬЗУЕМ ИМПОРТИРОВАННУЮ ФУНКЦИЮ ИЗ report_service !!!
            message = format_pr_message(payload)
            if message:
                await send_pr_notification(message)
                return {"status": "ok", "event": "pull_request"}
        else:
            log.info(f"ℹ️ Неподдерживаемый event: {event_type}")
            return {"status": "ignored", "reason": "unsupported_event"}

    except Exception as e:
        log.error(f"❌ Ошибка валидации данных GitHub: {e}")
        return {"status": "error", "reason": "invalid_schema", "details": str(e)}

    return {"status": "ignored", "reason": "no_message"}


