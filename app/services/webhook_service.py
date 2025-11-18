from fastapi import Request, HTTPException
from loguru import logger as log
import hashlib, hmac

from app.core.config import GITHUB_WEBHOOK_SECRET
from app.schemas.github_payload import GitHubPullRequestPayload, GitHubPushPayload
from app.services.sender_service import send_to_channel

async def verify_signature(request: Request):
    if not GITHUB_WEBHOOK_SECRET:
        log.warning("GITHUB_WEBHOOK_SECRET не задан! Проверка подписи пропущена.")
        return

    signature_header = request.headers.get("X-Hub-Signature-256")
    if not signature_header:
        raise HTTPException(status_code=403, detail="Signature header is missing")

    body = await request.body()
    expected = "sha256=" + hmac.new(GITHUB_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(status_code=403, detail="Invalid signature")

async def process_github_payload(request: Request):
    await verify_signature(request)
    event_type = request.headers.get("X-GitHub-Event")
    json_data = await request.json()

    try:
        if event_type == "push":
            payload = GitHubPushPayload(**json_data)
            message = _format_push_message(payload)
        elif event_type == "pull_request":
            payload = GitHubPullRequestPayload(**json_data)
            message = _format_pr_message(payload)
        else:
            log.info(f"Неподдерживаемый event {event_type}")
            return {"status": "ignored", "reason": "unsupported_event"}
    except Exception as e:
        log.error(f"Ошибка валидации данных GitHub: {e}")
        return {"status": "ignored", "reason": "invalid_schema"}

    if message:
        await send_to_channel(message)
        return {"status": "ok"}
    return {"status": "ignored", "reason": "no_message"}

# --- Форматирование сообщений ---
def _format_pr_message(payload: GitHubPullRequestPayload) -> str | None:
    pr = payload.pull_request
    repo = payload.repository
    user = pr.user
    action = payload.action

    if action == "opened":
        emoji, status = "🟢", "New Pull Request"
    elif action == "closed":
        emoji, status = ("🟣", "PR Merged") if pr.merged else ("🔴", "PR Closed")
    elif action == "reopened":
        emoji, status = "🔄", "PR Reopened"
    else:
        return None

    text = (
        f"{emoji} <b>{status}</b> | <a href='{repo.html_url}'>{repo.full_name}</a>\n"
        f"📝 <b>{pr.title}</b>\n"
        f"👤 Автор: <a href='{user.html_url}'>{user.login}</a>\n"
    )
    if pr.body:
        short_body = pr.body[:200] + "..." if len(pr.body) > 200 else pr.body
        short_body = short_body.replace("<", "&lt;").replace(">", "&gt;")
        text += f"\n<i>{short_body}</i>\n"
    text += f"\n🔗 <a href='{pr.html_url}'>Открыть Pull Request</a>"
    return text

def _format_push_message(payload: GitHubPushPayload) -> str:
    repo = payload.repository
    pusher = payload.pusher
    commits = payload.commits

    text = f"📦 <b>Push в {repo.full_name}</b> | Автор: <a href='{pusher.html_url}'>{pusher.login}</a>\n\n"
    for c in commits:
        text += f"💬 <a href='{c.url}'>{c.message}</a>\n"
    return text
