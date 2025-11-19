from fastapi import Request, HTTPException
from loguru import logger as log
import hashlib
import hmac

from app.core.config import GITHUB_WEBHOOK_SECRET

# Импортируем схемы данных
from app.schemas.github_payload import (
    GitHubPullRequestPayload,
    GitHubPushPayload,
    GitHubIssueCommentPayload,
    GitHubPullRequestReviewPayload,
    GitHubIssuesPayload,
    GitHubCheckRunPayload,
    GitHubReleasePayload,
)

# Импортируем функции отправки
from app.services.sender_service import (
    send_pr_notification,
    send_push_notification,
    send_comment_notification,
    send_pr_review_notification,
    send_issues_notification,
    send_cicd_notification,
    send_releases_notification,
)

# Импортируем функции форматирования
from app.services.report_service import (
    format_pr_message,
    format_push_message,
    format_comment_message,
    format_pr_review_message,
    format_issues_message,
    format_check_run_message,
    format_release_message,
)

# ============================================================================
# DISPATCHER CONFIGURATION
# ============================================================================

# Карта событий: Event Name -> (Schema Class, Formatter Function, Sender Function)
EVENT_HANDLERS = {
    "push": (
        GitHubPushPayload,
        format_push_message,
        send_push_notification
    ),
    "pull_request": (
        GitHubPullRequestPayload,
        format_pr_message,
        send_pr_notification
    ),
    "issue_comment": (
        GitHubIssueCommentPayload,
        format_comment_message,
        send_comment_notification
    ),
    "pull_request_review": (
        GitHubPullRequestReviewPayload,
        format_pr_review_message,
        send_pr_review_notification
    ),
    "issues": (
        GitHubIssuesPayload,
        format_issues_message,
        send_issues_notification
    ),
    "check_run": (
        GitHubCheckRunPayload,
        format_check_run_message,
        send_cicd_notification
    ),
    "release": (
        GitHubReleasePayload,
        format_release_message,
        send_releases_notification
    ),
}


# ============================================================================
# WEBHOOK LOGIC
# ============================================================================

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
    """Универсальная функция обработки webhook"""

    # 1. Проверяем подпись
    await verify_signature(request)

    # 2. Получаем тип события и JSON
    event_type = request.headers.get("X-GitHub-Event")
    json_data = await request.json()

    log.info(f"📨 Получен webhook: {event_type}")

    # 3. Ищем обработчик в карте
    handler_data = EVENT_HANDLERS.get(event_type)

    if not handler_data:
        log.info(f"ℹ️ Неподдерживаемый event: {event_type}")
        return {"status": "ignored", "reason": "unsupported_event"}

    # 4. Распаковываем инструменты и запускаем обработку
    payload_class, formatter_func, sender_func = handler_data

    try:
        # А. Валидация (превращаем JSON в Pydantic объект)
        # extra='ignore' в моделях спасет от ошибок валидации
        payload = payload_class(**json_data)

        # Б. Форматирование (получаем текст сообщения)
        message = formatter_func(payload)

        # В. Отправка (если форматтер вернул текст)
        if message:
            success = await sender_func(message)
            status = "ok" if success else "send_error"
            return {"status": status, "event": event_type}

        # Если форматтер вернул None (например, action='edited' и мы его игнорируем)
        return {"status": "ignored", "reason": "no_message_generated"}

    except Exception as e:
        log.exception(f"❌ Ошибка обработки события {event_type}: {e}")
        return {"status": "error", "reason": "exception", "details": str(e)}