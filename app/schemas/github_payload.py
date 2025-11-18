# app/schemas/github_payload.py
from typing import Optional
from pydantic import BaseModel, Field


# --- Вложенные модели (детали) ---

class GitHubUser(BaseModel):
    """Пользователь GitHub (автор PR)"""
    login: str
    html_url: str


class Repository(BaseModel):
    """Репозиторий, где происходит действие"""
    full_name: str  # например, "aiogram/aiogram"
    html_url: str


class PullRequest(BaseModel):
    """Сама сущность Pull Request"""
    html_url: str
    title: str
    state: str
    body: Optional[str] = None  # Описание PR (может быть пустым)
    user: GitHubUser
    merged: bool = False  # Важно: чтобы понять, PR закрыт или СМЕРЖЕН


# --- Основная модель (Payload) ---

class GitHubPayload(BaseModel):
    """
    Главная модель, описывающая JSON, который присылает GitHub.
    Мы берем только action, pull_request и repository.
    """
    action: str  # opened, closed, reopened, synchronize...
    pull_request: PullRequest
    repository: Repository

    # Иногда GitHub шлет "sender" (кто нажал кнопку),
    # но обычно нам хватает автора PR (pull_request.user).