from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityRead
from app.services.jobs import create_job
from app.workers.tasks_scoring import compute_opportunities

router = APIRouter(prefix="/projects/{project_id}/scoring", tags=["scoring"])


@router.post("/opportunities")
def enqueue_opportunity_scoring(project_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    job = create_job(db, project_id, "compute_opportunities")
    compute_opportunities.delay(str(project_id), str(job.id))
    return {"job_id": str(job.id)}


@router.get("/opportunities", response_model=list[OpportunityRead])
def list_opportunities(project_id: UUID, db: Session = Depends(get_db)) -> list[Opportunity]:
    stmt = (
        select(Opportunity)
        .where(Opportunity.project_id == project_id)
        .order_by(desc(Opportunity.score), desc(Opportunity.impressions))
    )
    return list(db.scalars(stmt).all())
