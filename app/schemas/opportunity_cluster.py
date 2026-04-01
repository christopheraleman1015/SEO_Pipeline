from uuid import UUID

from app.schemas.common import TimestampedModel


class OpportunityClusterRead(TimestampedModel):
    id: UUID
    project_id: UUID
    page_id: UUID | None
    label: str
    normalized_url: str | None
    query_count: int
    clicks: int
    impressions: int
    ctr: float
    avg_position: float | None
    score: float
    primary_query: str
    query_examples: str
    reason: str | None
