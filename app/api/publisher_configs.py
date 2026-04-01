from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.project import Project
from app.schemas.project_publisher_config import (
    ProjectPublisherConfigRead,
    ProjectPublisherConfigUpsert,
)
from app.services.publisher_configs import (
    get_project_publisher_config,
    upsert_project_publisher_config,
)

router = APIRouter(prefix="/projects/{project_id}/publisher-config", tags=["publisher-config"])


@router.get("", response_model=ProjectPublisherConfigRead)
def read_publisher_config(project_id: UUID, db: Session = Depends(get_db)) -> ProjectPublisherConfigRead:
    config = get_project_publisher_config(db, str(project_id))
    if not config:
        raise HTTPException(status_code=404, detail="Publisher config not found")
    return config


@router.put("", response_model=ProjectPublisherConfigRead)
def put_publisher_config(
    project_id: UUID,
    payload: ProjectPublisherConfigUpsert,
    db: Session = Depends(get_db),
) -> ProjectPublisherConfigRead:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return upsert_project_publisher_config(
        db,
        str(project_id),
        provider=payload.provider,
        mode=payload.mode,
        config_json=payload.config_json,
    )
