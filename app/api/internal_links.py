from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.internal_link_opportunity import InternalLinkOpportunity
from app.schemas.internal_link_opportunity import InternalLinkOpportunityRead
from app.services.jobs import create_job
from app.workers.tasks_internal_links import compute_internal_link_opportunities

router = APIRouter(prefix="/projects/{project_id}/internal-links", tags=["internal-links"])


@router.post("/opportunities")
def enqueue_internal_link_opportunities(
    project_id: UUID, db: Session = Depends(get_db)
) -> dict[str, str]:
    job = create_job(db, project_id, "compute_internal_link_opportunities")
    compute_internal_link_opportunities.delay(str(project_id), str(job.id))
    return {"job_id": str(job.id)}


@router.get("/opportunities", response_model=list[InternalLinkOpportunityRead])
def list_internal_link_opportunities(
    project_id: UUID, db: Session = Depends(get_db)
) -> list[InternalLinkOpportunity]:
    stmt = (
        select(InternalLinkOpportunity)
        .where(InternalLinkOpportunity.project_id == project_id)
        .order_by(desc(InternalLinkOpportunity.score), desc(InternalLinkOpportunity.target_score))
    )
    return list(db.scalars(stmt).all())
