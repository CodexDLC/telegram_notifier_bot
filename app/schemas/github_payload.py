# app/schemas/github_payload.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

# --- Базовая модель (если ты её уже внедрил, используй её, иначе ConfigDict в каждой) ---
class GitHubBaseModel(BaseModel):
    model_config = ConfigDict(extra='ignore')

# --- Вложенные модели ---
class GitHubUser(GitHubBaseModel):
    login: str
    html_url: str

class GitHubPusher(GitHubBaseModel):
    name: str
    email: str

class Repository(GitHubBaseModel):
    full_name: str
    html_url: str

class PullRequest(GitHubBaseModel):
    html_url: str
    title: str
    state: str
    body: Optional[str] = None
    user: GitHubUser
    merged: bool = False

class Commit(GitHubBaseModel):
    id: str
    message: str
    url: str

class Review(GitHubBaseModel):
    html_url: str
    state: str
    body: Optional[str] = None
    user: GitHubUser
    submitted_at: Optional[str] = None

class Issue(GitHubBaseModel):
    html_url: str
    number: int
    title: str
    state: str
    body: Optional[str] = None
    user: GitHubUser
    labels: Optional[List[dict]] = None
    assignees: Optional[List[GitHubUser]] = None
    # ВАЖНО: Это поле позволяет понять, это PR или просто Issue
    pull_request: Optional[Dict[str, Any]] = None

class Comment(GitHubBaseModel):
    """GitHub Comment"""
    html_url: str
    body: str
    user: GitHubUser
    created_at: Optional[str] = None

class CheckRun(GitHubBaseModel):
    name: str
    status: str
    conclusion: Optional[str] = None
    html_url: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class Release(GitHubBaseModel):
    html_url: str
    tag_name: str
    name: Optional[str] = None
    body: Optional[str] = None
    draft: bool = False
    prerelease: bool = False
    author: GitHubUser

# --- Payloads ---

class GitHubPullRequestPayload(GitHubBaseModel):
    action: str
    pull_request: PullRequest
    repository: Repository

class GitHubPushPayload(GitHubBaseModel):
    ref: str
    before: str
    after: str
    repository: Repository
    pusher: GitHubPusher
    sender: GitHubUser
    commits: List[Commit]
    head_commit: Optional[Commit] = None

class GitHubPullRequestReviewPayload(GitHubBaseModel):
    action: str
    review: Review
    pull_request: PullRequest
    repository: Repository

class GitHubIssuesPayload(GitHubBaseModel):
    action: str
    issue: Issue
    repository: Repository

class GitHubCheckRunPayload(GitHubBaseModel):
    action: str
    check_run: CheckRun
    repository: Repository

class GitHubReleasePayload(GitHubBaseModel):
    action: str
    release: Release
    repository: Repository

class GitHubIssueCommentPayload(GitHubBaseModel):
    """Payload для события issue_comment"""
    action: str
    comment: Comment
    issue: Issue
    repository: Repository
    sender: GitHubUser