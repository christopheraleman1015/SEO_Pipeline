from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import TimestampedModel


class ProjectPublisherConfigUpsert(BaseModel):
    provider: str
    mode: str = "draft"
    config_json: dict


class ProjectPublisherConfigRead(TimestampedModel):
    id: UUID
    project_id: UUID
    provider: str
    mode: str
    config_json: dict
