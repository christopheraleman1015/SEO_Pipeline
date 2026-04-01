from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import TimestampedModel


class ProjectCreate(BaseModel):
    name: str
    domain: str
    locale: str = "en-US"
    timezone: str = "America/Chicago"
    cms_type: str | None = None


class ProjectRead(TimestampedModel):
    id: UUID
    name: str
    domain: str
    locale: str
    timezone: str
    cms_type: str | None
