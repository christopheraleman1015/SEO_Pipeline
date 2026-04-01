from enum import StrEnum


class IssueSeverity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueCategory(StrEnum):
    CRAWL = "crawl"
    INDEXING = "indexing"
    ARCHITECTURE = "architecture"
    PERFORMANCE = "performance"
    CONTENT = "content"
    LINKS = "links"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class BriefStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"


class DraftStatus(StrEnum):
    DRAFT = "draft"
    QA_FAILED = "qa_failed"
    READY_FOR_REVIEW = "ready_for_review"
    APPROVED = "approved"
    PUBLISHED = "published"
