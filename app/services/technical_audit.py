from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import IssueCategory, IssueSeverity
from app.models.page import Page
from app.services.issues import clear_project_issues, create_issue
from app.services.normalization import normalize_url
from app.utils.ids import as_uuid


def run_audit_rules(db: Session, project_id: str) -> dict:
    project_uuid = as_uuid(project_id)
    pages = list(db.scalars(select(Page).where(Page.project_id == project_uuid)).all())
    clear_project_issues(db, project_id, IssueCategory.CRAWL)
    clear_project_issues(db, project_id, IssueCategory.INDEXING)
    clear_project_issues(db, project_id, IssueCategory.CONTENT)

    issues_created = 0
    seen_titles: dict[str, list[Page]] = {}
    seen_h1s: dict[str, list[Page]] = {}

    for page in pages:
        if page.title:
            seen_titles.setdefault(page.title.strip().lower(), []).append(page)
        if page.h1:
            seen_h1s.setdefault(page.h1.strip().lower(), []).append(page)

        if page.http_status and page.http_status >= 400:
            create_issue(
                db,
                project_id,
                str(page.id),
                "http_error",
                IssueSeverity.CRITICAL,
                IssueCategory.CRAWL,
                {"url": page.url, "http_status": page.http_status},
            )
            issues_created += 1

        if page.indexable is False:
            create_issue(
                db,
                project_id,
                str(page.id),
                "non_indexable_page",
                IssueSeverity.HIGH,
                IssueCategory.INDEXING,
                {"url": page.url, "meta_robots": page.meta_robots},
            )
            issues_created += 1

        if page.canonical_url:
            try:
                normalized_canonical = normalize_url(page.canonical_url)
            except ValueError:
                normalized_canonical = page.canonical_url
            if normalized_canonical != page.normalized_url:
                create_issue(
                    db,
                    project_id,
                    str(page.id),
                    "canonical_mismatch",
                    IssueSeverity.MEDIUM,
                    IssueCategory.INDEXING,
                    {"url": page.url, "canonical_url": page.canonical_url},
                )
                issues_created += 1

        if not page.title:
            create_issue(
                db,
                project_id,
                str(page.id),
                "missing_title",
                IssueSeverity.MEDIUM,
                IssueCategory.CONTENT,
                {"url": page.url},
            )
            issues_created += 1

        if not page.h1:
            create_issue(
                db,
                project_id,
                str(page.id),
                "missing_h1",
                IssueSeverity.MEDIUM,
                IssueCategory.CONTENT,
                {"url": page.url},
            )
            issues_created += 1

        if page.word_count is not None and page.word_count < 200:
            create_issue(
                db,
                project_id,
                str(page.id),
                "thin_content",
                IssueSeverity.LOW,
                IssueCategory.CONTENT,
                {"url": page.url, "word_count": page.word_count},
            )
            issues_created += 1

    for title, title_pages in seen_titles.items():
        if title and len(title_pages) > 1:
            for page in title_pages:
                create_issue(
                    db,
                    project_id,
                    str(page.id),
                    "duplicate_title",
                    IssueSeverity.MEDIUM,
                    IssueCategory.CONTENT,
                    {"url": page.url, "title": page.title},
                )
                issues_created += 1

    for h1, h1_pages in seen_h1s.items():
        if h1 and len(h1_pages) > 1:
            for page in h1_pages:
                create_issue(
                    db,
                    project_id,
                    str(page.id),
                    "duplicate_h1",
                    IssueSeverity.LOW,
                    IssueCategory.CONTENT,
                    {"url": page.url, "h1": page.h1},
                )
                issues_created += 1

    db.commit()
    return {"project_id": project_id, "issues_created": issues_created, "pages_scanned": len(pages)}
