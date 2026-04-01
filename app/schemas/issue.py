from datetime import datetime
from uuid import UUID

from app.schemas.common import ORMBaseModel


class IssueRead(ORMBaseModel):
    id: UUID
    project_id: UUID
    page_id: UUID | None
    issue_type: str
    severity: str
    category: str
    status: str
    details: dict
    detected_at: datetime
