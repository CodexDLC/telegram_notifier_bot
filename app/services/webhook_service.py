# app/services/webhook_service.py
import hashlib
import hmac
import json
from fastapi import Request, HTTPException
from loguru import logger as log

from app.core.config import GITHUB_WEBHOOK_SECRET
from app.schemas.github_payload import GitHubPayload
from app.services.sender_service import send_to_channel


async def verify_signature(request: Request):
    """
    Проверяет, что запрос действительно пришел от GitHub,
    используя секретный ключ (HMAC SHA-256).
    """
    if not GITHUB_WEBHOOK_SECRET:
        log.warning("GITHUB_WEBHOOK_SECRET не задан! Проверка подписи пропущена (ОПАСНО).")
        return

    # 1. Получаем подпись из заголовка
    signature_header = request.headers.get("X-Hub-Signature-256")
    if not signature_header:
        raise HTTPException(status_code=403, detail="Signature header is missing")

    # 2. Читаем тело запроса (raw bytes)
    body = await request.body()

    # 3. Считаем хеш сами, используя наш Секрет
    hash_object = hmac.new(
        key=GITHUB_WEBHOOK_SECRET.encode(),
        msg=body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()

    # 4. Сравниваем (безопасным методом, чтобы избежать timing attacks)
    if not hmac.compare_digest(expected_signature, signature_header):
        log.error("Неверная подпись вебхука! Возможно, атака.")
        raise HTTPException(status_code=403, detail="Invalid signature")


async def process_github_payload(request: Request):
    """
    Основная логика обработки вебхука.
    """
    # 1. Проверка безопасности
    await verify_signature(request)

    # 2. Парсинг JSON через Pydantic
    try:
        json_data = await request.json()
        payload = GitHubPayload(**json_data)  # Валидация схемы
    except Exception as e:
        log.error(f"Ошибка валидации данных GitHub: {e}")
        # Не ломаем GitHub (вернем 200), но логируем ошибку
        return {"status": "ignored", "reason": "invalid_schema"}

    # 3. Форматирование сообщения
    message = _format_message(payload)
    if not message:
        return {"status": "ignored", "reason": "unsupported_action"}

    # 4. Отправка в Telegram
    await send_to_channel(message)
    return {"status": "ok"}


def _format_message(payload: GitHubPayload) -> str | None:
    """
    Превращает сухие данные в красивый HTML-текст для Телеграма.
    """
    pr = payload.pull_request
    repo = payload.repository
    user = pr.user
    action = payload.action

    # Эмодзи и заголовки для разных действий
    if action == "opened":
        emoji = "🟢"
        status = "New Pull Request"
    elif action == "closed":
        if pr.merged:
            emoji = "🟣"
            status = "PR Merged"
        else:
            emoji = "🔴"
            status = "PR Closed (Rejected)"
    elif action == "reopened":
        emoji = "🔄"
        status = "PR Reopened"
    else:
        # Остальные действия (edited, labeled и т.д.) игнорируем, чтобы не спамить
        return None

    # Сборка HTML сообщения
    text = (
        f"{emoji} <b>{status}</b> | <a href='{repo.html_url}'>{repo.full_name}</a>\n\n"
        f"📝 <b>{pr.title}</b>\n"
        f"👤 Автор: <a href='{user.html_url}'>{user.login}</a>\n"
    )

    # Если есть описание PR, добавляем его (обрезаем, если длинное)
    if pr.body:
        short_body = pr.body[:200] + "..." if len(pr.body) > 200 else pr.body
        # Экранируем HTML-теги в описании, чтобы не сломать разметку бота
        short_body = short_body.replace("<", "&lt;").replace(">", "&gt;")
        text += f"\n<i>{short_body}</i>\n"

    text += f"\n🔗 <a href='{pr.html_url}'>Открыть Pull Request</a>"

    return text