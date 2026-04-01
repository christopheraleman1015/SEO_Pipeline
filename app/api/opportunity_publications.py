from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.opportunity_draft import OpportunityDraft
from app.models.opportunity_publication import OpportunityPublication
from app.schemas.opportunity_publication import OpportunityPublicationRead
from app.services.jobs import create_job
from app.services.opportunity_publications import (
    _latest_publication,
    _latest_review,
    approve_opportunity_draft_for_publish,
)
from app.workers.tasks_opportunity_publications import publish_opportunity_draft

router = APIRouter(tags=["opportunity-publications"])


@router.post("/opportunity-drafts/{draft_id}/approve", response_model=OpportunityPublicationRead)
def approve_opportunity_draft(draft_id: UUID, db: Session = Depends(get_db)) -> OpportunityPublication:
    try:
        return approve_opportunity_draft_for_publish(db, str(draft_id))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/opportunity-drafts/{draft_id}/publish")
def enqueue_opportunity_publish(draft_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    draft = db.get(OpportunityDraft, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Opportunity draft not found")
    review = _latest_review(db, str(draft_id))
    if not review or not review.review_json.get("publish_ready"):
        raise HTTPException(status_code=400, detail="Draft is not publish-ready")
    publication = _latest_publication(db, str(draft_id))
    if not publication or not publication.approved_for_publish:
        raise HTTPException(status_code=400, detail="Draft has not been approved for publish")

    job = create_job(
        db,
        draft.project_id,
        "publish_opportunity_draft",
        payload={"draft_id": str(draft_id)},
    )
    publish_opportunity_draft.delay(str(draft_id), str(job.id))
    return {"job_id": str(job.id)}


@router.get("/opportunity-drafts/{draft_id}/publication/latest", response_model=OpportunityPublicationRead)
def get_latest_opportunity_publication(
    draft_id: UUID, db: Session = Depends(get_db)
) -> OpportunityPublication:
    publication = db.scalar(
        select(OpportunityPublication)
        .where(OpportunityPublication.opportunity_draft_id == draft_id)
        .order_by(desc(OpportunityPublication.created_at))
        .limit(1)
    )
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    return publication
