# app/services/report_service.py
"""
Сервис для форматирования GitHub событий в красивые сообщения
"""
from loguru import logger as log

from app.schemas.github_payload import (
    GitHubPullRequestPayload,
    GitHubPushPayload,
    GitHubPullRequestReviewPayload,
    GitHubIssuesPayload,
    GitHubCheckRunPayload,
    GitHubReleasePayload,
    PullRequest,
    Repository,
    Review,
    Issue,
    CheckRun,
    Release,
    Commit,
    GitHubUser,
)


# ============================================================================
# PULL REQUESTS
# ============================================================================

def format_pr_message(payload: GitHubPullRequestPayload) -> str | None:
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


# ============================================================================
# PULL REQUEST REVIEWS
# ============================================================================

def format_pr_review_message(payload: GitHubPullRequestReviewPayload) -> str | None:
    """Форматирует сообщение о ревью PR"""
    review = payload.review
    pr = payload.pull_request
    repo = payload.repository
    action = payload.action

    if action != "submitted":
        return None

    # Определяем тип ревью
    state = review.state.lower()
    if state == "approved":
        emoji, status = "✅", "Одобрил PR"
        color = "🟢"
    elif state == "changes_requested":
        emoji, status = "🔴", "Запросил изменения"
        color = "🔴"
    elif state == "commented":
        emoji, status = "💬", "Оставил комментарий"
        color = "🟡"
    else:
        return None

    text = (
        f"{emoji} <b>{status}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>PR:</b> <a href='{pr.html_url}'>{pr.title}</a>\n"
        f"👤 <b>Ревьюер:</b> <a href='{review.user.html_url}'>@{review.user.login}</a>\n"
    )

    # Добавляем комментарий, если есть
    if review.body:
        short_body = review.body[:150] + "..." if len(review.body) > 150 else review.body
        short_body = short_body.replace("<", "&lt;").replace(">", "&gt;")
        text += f"\n💭 <i>{short_body}</i>\n"

    text += f"\n🔗 <a href='{review.html_url}'>Посмотреть ревью</a>"

    return text


# ============================================================================
# PUSHES
# ============================================================================

def format_push_message(payload: GitHubPushPayload) -> str | None:
    """Форматирует красивое сообщение о Push"""
    repo = payload.repository
    sender = payload.sender
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


# ============================================================================
# ISSUES
# ============================================================================

def format_issues_message(payload: GitHubIssuesPayload) -> str | None:
    """Форматирует сообщение об Issues"""
    issue = payload.issue
    repo = payload.repository
    action = payload.action

    # Определяем emoji и статус
    if action == "opened":
        emoji, status = "🐛", "Новая задача"
    elif action == "closed":
        emoji, status = "✅", "Задача закрыта"
    elif action == "reopened":
        emoji, status = "🔄", "Задача переоткрыта"
    else:
        log.debug(f"Issue action '{action}' игнорируется")
        return None

    text = (
        f"{emoji} <b>{status} #{issue.number}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Репозиторий:</b> <a href='{repo.html_url}'>{repo.full_name}</a>\n"
        f"📝 <b>Название:</b> {issue.title}\n"
        f"👤 <b>Автор:</b> <a href='{issue.user.html_url}'>@{issue.user.login}</a>\n"
    )

    # Добавляем описание
    if issue.body:
        short_body = issue.body[:200] + "..." if len(issue.body) > 200 else issue.body
        short_body = short_body.replace("<", "&lt;").replace(">", "&gt;")
        text += f"\n💬 <i>{short_body}</i>\n"

    text += f"\n🔗 <a href='{issue.html_url}'>Открыть задачу</a>"

    return text


# ============================================================================
# CHECK RUNS (CI/CD)
# ============================================================================

def format_check_run_message(payload: GitHubCheckRunPayload) -> str | None:
    """Форматирует сообщение о Check Run (CI/CD)"""
    check = payload.check_run
    repo = payload.repository
    action = payload.action

    # Интересуют только завершенные проверки
    if action != "completed" or check.status != "completed":
        return None

    # Определяем результат
    conclusion = check.conclusion
    if conclusion == "success":
        emoji, status = "✅", "Тесты пройдены"
    elif conclusion == "failure":
        emoji, status = "❌", "Тесты провалены"
    elif conclusion == "cancelled":
        emoji, status = "⚠️", "Тесты отменены"
    elif conclusion == "skipped":
        emoji, status = "⏭", "Тесты пропущены"
    else:
        emoji, status = "🔵", f"Статус: {conclusion}"

    text = (
        f"{emoji} <b>{status}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Репозиторий:</b> <a href='{repo.html_url}'>{repo.full_name}</a>\n"
        f"🔧 <b>Проверка:</b> {check.name}\n"
        f"\n🔗 <a href='{check.html_url}'>Посмотреть детали</a>"
    )

    return text


# ============================================================================
# RELEASES
# ============================================================================

def format_release_message(payload: GitHubReleasePayload) -> str | None:
    """Форматирует сообщение о Release"""
    release = payload.release
    repo = payload.repository
    action = payload.action

    # Интересует только публикация
    if action != "published":
        return None

    # Определяем тип релиза
    if release.prerelease:
        emoji, status = "🧪", "Pre-release опубликован"
    elif release.draft:
        emoji, status = "📝", "Draft release"
    else:
        emoji, status = "🚀", "Новый релиз"

    text = (
        f"{emoji} <b>{status}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Репозиторий:</b> <a href='{repo.html_url}'>{repo.full_name}</a>\n"
        f"🏷 <b>Версия:</b> <code>{release.tag_name}</code>\n"
    )

    if release.name:
        text += f"📝 <b>Название:</b> {release.name}\n"

    # Добавляем changelog
    if release.body:
        short_body = release.body[:300] + "..." if len(release.body) > 300 else release.body
        short_body = short_body.replace("<", "&lt;").replace(">", "&gt;")
        text += f"\n📜 <b>Changelog:</b>\n<i>{short_body}</i>\n"

    text += f"\n🔗 <a href='{release.html_url}'>Посмотреть релиз</a>"

    return text