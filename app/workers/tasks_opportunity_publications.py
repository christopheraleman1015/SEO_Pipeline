from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.services.jobs import mark_job_completed, mark_job_failed, mark_job_running
from app.services.opportunity_publications import publish_approved_draft
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks_opportunity_publications.publish_opportunity_draft")
def publish_opportunity_draft(draft_id: str, job_id: str | None) -> dict:
    db: Session = SessionLocal()
    try:
        if job_id:
            mark_job_running(db, job_id)
        publication = publish_approved_draft(db, draft_id)
        if job_id:
            mark_job_completed(db, job_id, output_ref=str(publication.id))
        return {"publication_id": str(publication.id), "draft_id": draft_id}
    except Exception as exc:
        if job_id:
            mark_job_failed(db, job_id, str(exc))
        raise
    finally:
        db.close()
