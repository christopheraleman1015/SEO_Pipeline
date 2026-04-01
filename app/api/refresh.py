from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.jobs import create_job
from app.workers.tasks_refresh import detect_content_decay, suggest_refresh_actions

router = APIRouter(prefix="/projects/{project_id}/refresh", tags=["refresh"])


@router.post("/detect")
def enqueue_refresh_detection(project_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    job = create_job(db, project_id, "detect_content_decay")
    detect_content_decay.delay(str(project_id), str(job.id))
    return {"job_id": str(job.id)}


@router.get("/candidates")
def list_refresh_candidates(project_id: UUID) -> dict[str, str]:
    return {"project_id": str(project_id), "status": "candidates_pending"}


@router.post("/suggest")
def enqueue_refresh_suggestions(project_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    job = create_job(db, project_id, "suggest_refresh_actions")
    suggest_refresh_actions.delay(str(project_id), str(job.id))
    return {"job_id": str(job.id)}
