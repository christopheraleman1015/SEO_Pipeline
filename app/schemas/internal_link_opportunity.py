from uuid import UUID

from app.schemas.common import TimestampedModel


class InternalLinkOpportunityRead(TimestampedModel):
    id: UUID
    project_id: UUID
    source_page_id: UUID | None
    target_page_id: UUID | None
    cluster_id: UUID | None
    source_url: str
    target_url: str
    suggested_anchor: str
    overlap_score: float
    target_score: float
    score: float
    reason: str | None
