from uuid import UUID

from app.schemas.common import TimestampedModel


class ClusterRead(TimestampedModel):
    id: UUID
    project_id: UUID
    label: str
    primary_intent: str | None
    target_page_type: str | None
    target_page_id: UUID | None
    score: float | None
    status: str
