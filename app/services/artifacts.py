from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.artifact import Artifact
from app.storage.artifacts import build_artifact_path
from app.utils.hashing import sha256_text


def create_artifact_record(
    db: Session,
    project_id: UUID | str,
    artifact_type: str,
    source_name: str,
    content: bytes,
) -> Artifact:
    destination = build_artifact_path(str(project_id), artifact_type, source_name)
    destination.write_bytes(content)

    artifact = Artifact(
        project_id=project_id,
        artifact_type=artifact_type,
        storage_path=str(destination),
        content_hash=sha256_text(content.decode("utf-8", errors="ignore")),
        artifact_metadata={"source_name": source_name, "size": len(content)},
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


def resolve_artifact_path(artifact: Artifact) -> Path:
    return Path(artifact.storage_path)
