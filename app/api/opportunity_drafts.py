from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.opportunity_brief import OpportunityBrief
from app.models.opportunity_draft import OpportunityDraft
from app.schemas.opportunity_draft import OpportunityDraftRead
from app.services.jobs import create_job
from app.workers.tasks_opportunity_drafts import generate_brief_draft

router = APIRouter(tags=["opportunity-drafts"])


@router.post("/opportunity-briefs/{brief_id}/drafts")
def enqueue_opportunity_draft(brief_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    brief = db.get(OpportunityBrief, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Opportunity brief not found")

    job = create_job(
        db,
        brief.project_id,
        "generate_opportunity_draft",
        payload={"brief_id": str(brief_id)},
    )
    generate_brief_draft.delay(str(brief_id), str(job.id))
    return {"job_id": str(job.id)}


@router.get("/opportunity-briefs/{brief_id}/drafts/latest", response_model=OpportunityDraftRead)
def get_latest_opportunity_draft(brief_id: UUID, db: Session = Depends(get_db)) -> OpportunityDraft:
    draft = db.scalar(
        select(OpportunityDraft)
        .where(OpportunityDraft.opportunity_brief_id == brief_id)
        .order_by(desc(OpportunityDraft.version))
        .limit(1)
    )
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft
