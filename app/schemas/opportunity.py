from uuid import UUID

from app.schemas.common import TimestampedModel


class OpportunityRead(TimestampedModel):
    id: UUID
    project_id: UUID
    page_id: UUID | None
    keyword: str
    normalized_url: str | None
    clicks: int
    impressions: int
    ctr: float
    avg_position: float | None
    business_value: float
    freshness_need: float
    content_gap: float
    rankability: float
    score: float
    reason: str | None
