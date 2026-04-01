from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import TimestampedModel


class OpportunityEvidenceCreate(BaseModel):
    title: str
    content_text: str
    evidence_type: str = "note"


class OpportunityEvidenceRead(TimestampedModel):
    id: UUID
    project_id: UUID
    opportunity_brief_id: UUID
    artifact_id: UUID | None
    evidence_type: str
    title: str
    content_text: str | None
    metadata_json: dict
