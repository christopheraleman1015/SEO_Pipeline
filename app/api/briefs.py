from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.brief import Brief
from app.schemas.brief import BriefRead
from app.workers.tasks_briefs import generate_content_brief

router = APIRouter(tags=["briefs"])


@router.post("/clusters/{cluster_id}/briefs/generate")
def enqueue_generate_brief(cluster_id: UUID) -> dict[str, str]:
    task = generate_content_brief.delay(str(cluster_id), None)
    return {"job_id": task.id}


@router.get("/clusters/{cluster_id}/briefs/latest", response_model=BriefRead)
def get_latest_brief(cluster_id: UUID, db: Session = Depends(get_db)) -> Brief:
    brief = db.scalar(
        select(Brief).where(Brief.cluster_id == cluster_id).order_by(desc(Brief.version)).limit(1)
    )
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    return brief


@router.post("/briefs/{brief_id}/approve")
def approve_brief(brief_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    brief = db.get(Brief, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    brief.status = "approved"
    db.add(brief)
    db.commit()
    return {"brief_id": str(brief.id), "status": brief.status}
