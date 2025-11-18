# app/schemas/github_payload.py
from typing import Optional, List
from pydantic import BaseModel

# --- Общие вложенные модели ---
class GitHubUser(BaseModel):
    """Полная информация о пользователе GitHub (для PR, sender)"""
    login: str
    html_url: str


class GitHubPusher(BaseModel):
    """Информация о pusher (упрощенная, только name и email)"""
    name: str
    email: str


class Repository(BaseModel):
    full_name: str
    html_url: str


class PullRequest(BaseModel):
    html_url: str
    title: str
    state: str
    body: Optional[str] = None
    user: GitHubUser
    merged: bool = False


class Commit(BaseModel):
    id: str
    message: str
    url: str


class Review(BaseModel):
    """Pull Request Review"""
    html_url: str
    state: str  # approved, changes_requested, commented
    body: Optional[str] = None
    user: GitHubUser
    submitted_at: Optional[str] = None


class Issue(BaseModel):
    """GitHub Issue"""
    html_url: str
    number: int
    title: str
    state: str  # open, closed
    body: Optional[str] = None
    user: GitHubUser
    labels: Optional[List[dict]] = None
    assignees: Optional[List[GitHubUser]] = None


class CheckRun(BaseModel):
    """GitHub Check Run (CI/CD)"""
    name: str
    status: str  # queued, in_progress, completed
    conclusion: Optional[str] = None  # success, failure, neutral, cancelled, skipped, timed_out
    html_url: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class Release(BaseModel):
    """GitHub Release"""
    html_url: str
    tag_name: str
    name: Optional[str] = None
    body: Optional[str] = None
    draft: bool = False
    prerelease: bool = False
    author: GitHubUser


class Alert(BaseModel):
    """Dependabot/Security Alert"""
    html_url: str
    number: int
    state: str
    severity: Optional[str] = None
    summary: Optional[str] = None


# --- Основные модели Payload ---

class GitHubPullRequestPayload(BaseModel):
    action: str
    pull_request: PullRequest
    repository: Repository


class GitHubPushPayload(BaseModel):
    ref: str
    before: str
    after: str
    repository: Repository
    pusher: GitHubPusher
    sender: GitHubUser
    commits: List[Commit]
    head_commit: Optional[Commit] = None


# --- НОВЫЕ МОДЕЛИ (Исправление ошибки) ---

class GitHubPullRequestReviewPayload(BaseModel):
    action: str
    review: Review
    pull_request: PullRequest
    repository: Repository


class GitHubIssuesPayload(BaseModel):
    action: str
    issue: Issue
    repository: Repository


class GitHubCheckRunPayload(BaseModel):
    action: str
    check_run: CheckRun
    repository: Repository


class GitHubReleasePayload(BaseModel):
    action: str
    release: Release
    repository: Repository

# В зависимости от функционала, можно добавить и Payload для Alert
# class GitHubSecurityAlertPayload(BaseModel):
#     action: str
#     alert: Alert
#     repository: Repository