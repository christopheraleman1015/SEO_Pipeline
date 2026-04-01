from uuid import UUID

from app.schemas.common import TimestampedModel


class OpportunityBriefRead(TimestampedModel):
    id: UUID
    project_id: UUID
    opportunity_cluster_id: UUID
    target_page_id: UUID | None
    version: int
    status: str
    brief_json: dict
