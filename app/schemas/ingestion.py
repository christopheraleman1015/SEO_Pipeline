from uuid import UUID

from pydantic import BaseModel


class ArtifactUploadResponse(BaseModel):
    artifact_id: UUID
    job_id: str
