# app/schemas/github_payload.py
from typing import Optional, List
from pydantic import BaseModel

# --- Общие вложенные модели ---
class GitHubUser(BaseModel):
    login: str
    html_url: str

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


# --- Основная модель (Payload) ---

class GitHubPullRequestPayload(BaseModel):
    action: str
    pull_request: PullRequest
    repository: Repository

class GitHubPushPayload(BaseModel):
    ref: str
    before: str
    after: str
    repository: Repository
    pusher: GitHubUser
    sender: GitHubUser
    commits: List[Commit]
    head_commit: Optional[Commit]
