from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IDResponse(ORMBaseModel):
    id: UUID


class TimestampedModel(ORMBaseModel):
    created_at: datetime
    updated_at: datetime
