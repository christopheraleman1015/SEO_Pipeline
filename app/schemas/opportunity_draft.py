from uuid import UUID

from app.schemas.common import TimestampedModel


class OpportunityDraftRead(TimestampedModel):
    id: UUID
    project_id: UUID
    opportunity_brief_id: UUID
    target_page_id: UUID | None
    version: int
    status: str
    content_markdown: str
    qa_json: dict
