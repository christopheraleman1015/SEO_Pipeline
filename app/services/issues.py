from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.enums import IssueCategory, IssueSeverity
from app.models.issue import Issue
from app.utils.ids import as_uuid


def clear_project_issues(
    db: Session, project_id: UUID | str, category: IssueCategory | None = None
) -> None:
    stmt = delete(Issue).where(Issue.project_id == as_uuid(project_id))
    if category:
        stmt = stmt.where(Issue.category == category.value)
    db.execute(stmt)


def create_issue(
    db: Session,
    project_id: UUID | str,
    page_id: UUID | str | None,
    issue_type: str,
    severity: IssueSeverity,
    category: IssueCategory,
    details: dict,
) -> Issue:
    issue = Issue(
        project_id=as_uuid(project_id),
        page_id=as_uuid(page_id),
        issue_type=issue_type,
        severity=severity.value,
        category=category.value,
        details=details,
    )
    db.add(issue)
    return issue
