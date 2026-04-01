from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.services.jobs import mark_job_completed, mark_job_failed, mark_job_running
from app.services.opportunity_reviews import review_opportunity_draft
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks_opportunity_reviews.review_brief_draft")
def review_brief_draft(draft_id: str, job_id: str | None) -> dict:
    db: Session = SessionLocal()
    try:
        if job_id:
            mark_job_running(db, job_id)
        review = review_opportunity_draft(db, draft_id)
        if job_id:
            mark_job_completed(db, job_id, output_ref=str(review.id))
        return {"review_id": str(review.id), "draft_id": draft_id, "version": review.version}
    except Exception as exc:
        if job_id:
            mark_job_failed(db, job_id, str(exc))
        raise
    finally:
        db.close()
