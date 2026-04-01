from datetime import datetime
from uuid import UUID

from app.schemas.common import ORMBaseModel


class JobRead(ORMBaseModel):
    id: UUID
    project_id: UUID
    job_type: str
    status: str
    priority: int
    payload: dict
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    error_message: str | None
