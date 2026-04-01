from uuid import UUID

from app.schemas.common import TimestampedModel


class OpportunityReviewRead(TimestampedModel):
    id: UUID
    project_id: UUID
    opportunity_draft_id: UUID
    version: int
    status: str
    review_json: dict
