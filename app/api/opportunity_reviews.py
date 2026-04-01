from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.opportunity_draft import OpportunityDraft
from app.models.opportunity_review import OpportunityReview
from app.schemas.opportunity_review import OpportunityReviewRead
from app.services.jobs import create_job
from app.workers.tasks_opportunity_reviews import review_brief_draft

router = APIRouter(tags=["opportunity-reviews"])


@router.post("/opportunity-drafts/{draft_id}/review")
def enqueue_opportunity_review(draft_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    draft = db.get(OpportunityDraft, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Opportunity draft not found")

    job = create_job(
        db,
        draft.project_id,
        "review_opportunity_draft",
        payload={"draft_id": str(draft_id)},
    )
    review_brief_draft.delay(str(draft_id), str(job.id))
    return {"job_id": str(job.id)}


@router.get("/opportunity-drafts/{draft_id}/review/latest", response_model=OpportunityReviewRead)
def get_latest_opportunity_review(draft_id: UUID, db: Session = Depends(get_db)) -> OpportunityReview:
    review = db.scalar(
        select(OpportunityReview)
        .where(OpportunityReview.opportunity_draft_id == draft_id)
        .order_by(desc(OpportunityReview.version))
        .limit(1)
    )
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review
