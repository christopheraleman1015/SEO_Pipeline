from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.opportunity_draft import OpportunityDraft
from app.services.jobs import create_job
from app.workers.tasks_opportunity_revisions import revise_draft

router = APIRouter(tags=["opportunity-revisions"])


@router.post("/opportunity-drafts/{draft_id}/revise")
def enqueue_opportunity_revision(draft_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    draft = db.get(OpportunityDraft, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Opportunity draft not found")

    job = create_job(
        db,
        draft.project_id,
        "revise_opportunity_draft",
        payload={"draft_id": str(draft_id)},
    )
    revise_draft.delay(str(draft_id), str(job.id))
    return {"job_id": str(job.id)}
