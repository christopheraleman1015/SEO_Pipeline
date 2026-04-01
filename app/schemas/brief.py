from uuid import UUID

from app.schemas.common import TimestampedModel


class BriefRead(TimestampedModel):
    id: UUID
    project_id: UUID
    cluster_id: UUID
    target_page_id: UUID | None
    version: int
    status: str
    brief_json: dict
    prompt_version: str | None
