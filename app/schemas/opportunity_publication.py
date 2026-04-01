from uuid import UUID

from app.schemas.common import TimestampedModel


class OpportunityPublicationRead(TimestampedModel):
    id: UUID
    project_id: UUID
    opportunity_draft_id: UUID
    approved_for_publish: bool
    published: bool
    target_url: str | None
    publish_result_json: dict
