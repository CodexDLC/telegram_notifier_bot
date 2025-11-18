# app/services/webhook_service.py
from fastapi import Request, HTTPException
from loguru import logger as log
import hashlib
import hmac

from app.core.config import GITHUB_WEBHOOK_SECRET
from app.schemas.github_payload import (
    GitHubPullRequestPayload,
    GitHubPushPayload,
    GitHubPullRequestReviewPayload,
    GitHubIssuesPayload,
    GitHubCheckRunPayload,
    GitHubReleasePayload,
)
from app.services.sender_service import (
    send_pr_notification,
    send_push_notification,
    send_issues_notification,
    send_cicd_notification,
    send_releases_notification,
)
from app.services.report_service import (
    format_pr_message,
    format_push_message,
    format_pr_review_message,
    format_issues_message,
    format_check_run_message,
    format_release_message,
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
            message = _format_push_message(payload)
            if message:
                await send_push_notification(message)
                return {"status": "ok", "event": "push"}

        elif event_type == "pull_request":
            payload = GitHubPullRequestPayload(**json_data)
            message = _format_pr_message(payload)
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


# ============================================================================
# ФОРМАТИРОВАНИЕ СООБЩЕНИЙ
# ============================================================================

def _format_pr_message(payload: GitHubPullRequestPayload) -> str | None:
    """Форматирует красивое сообщение о Pull Request"""
    pr = payload.pull_request
    repo = payload.repository
    user = pr.user
    action = payload.action

    # Определяем emoji и статус
    if action == "opened":
        emoji, status = "🟢", "Новый Pull Request"
    elif action == "closed":
        emoji, status = ("🟣", "PR Смержен") if pr.merged else ("🔴", "PR Закрыт")
    elif action == "reopened":
        emoji, status = "🔄", "PR Переоткрыт"
    else:
        log.debug(f"PR action '{action}' игнорируется")
        return None

    # Формируем текст
    text = (
        f"{emoji} <b>{status}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Репозиторий:</b> <a href='{repo.html_url}'>{repo.full_name}</a>\n"
        f"📝 <b>Название:</b> {pr.title}\n"
        f"👤 <b>Автор:</b> <a href='{user.html_url}'>@{user.login}</a>\n"
    )

    # Добавляем описание, если есть
    if pr.body:
        short_body = pr.body[:200] + "..." if len(pr.body) > 200 else pr.body
        # Экранируем HTML
        short_body = short_body.replace("<", "&lt;").replace(">", "&gt;")
        text += f"\n💬 <i>{short_body}</i>\n"

    text += f"\n🔗 <a href='{pr.html_url}'>Открыть Pull Request</a>"

    return text


def _format_push_message(payload: GitHubPushPayload) -> str | None:
    """Форматирует красивое сообщение о Push"""
    repo = payload.repository
    pusher = payload.pusher
    sender = payload.sender  # Используем sender для ссылки на профиль
    commits = payload.commits
    ref = payload.ref

    # Извлекаем имя ветки из ref (refs/heads/main -> main)
    branch = ref.split('/')[-1] if '/' in ref else ref

    # Если коммитов нет, игнорируем
    if not commits:
        log.debug("Push без коммитов, игнорируется")
        return None

    # Формируем заголовок
    text = (
        f"📦 <b>Push в репозиторий</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷 <b>Репозиторий:</b> <a href='{repo.html_url}'>{repo.full_name}</a>\n"
        f"🌿 <b>Ветка:</b> <code>{branch}</code>\n"
        f"👤 <b>Автор:</b> <a href='{sender.html_url}'>@{sender.login}</a>\n"
        f"📊 <b>Коммитов:</b> {len(commits)}\n\n"
    )

    # Добавляем коммиты (максимум 5, чтобы не спамить)
    max_commits = 5
    for i, commit in enumerate(commits[:max_commits], 1):
        # Короткий хеш (первые 7 символов)
        short_sha = commit.id[:7]
        # Первая строка сообщения коммита
        commit_message = commit.message.split('\n')[0]
        # Обрезаем слишком длинные сообщения
        if len(commit_message) > 60:
            commit_message = commit_message[:60] + "..."

        text += f"{i}. <code>{short_sha}</code> {commit_message}\n"

    # Если коммитов больше, добавляем примечание
    if len(commits) > max_commits:
        text += f"\n<i>... и еще {len(commits) - max_commits} коммитов</i>\n"

    # Ссылка на сравнение
    if payload.before and payload.after:
        compare_url = f"{repo.html_url}/compare/{payload.before[:7]}...{payload.after[:7]}"
        text += f"\n🔗 <a href='{compare_url}'>Посмотреть изменения</a>"

    return text