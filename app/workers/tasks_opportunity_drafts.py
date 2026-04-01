from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.services.jobs import mark_job_completed, mark_job_failed, mark_job_running
from app.services.opportunity_drafts import generate_opportunity_draft
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks_opportunity_drafts.generate_brief_draft")
def generate_brief_draft(brief_id: str, job_id: str | None) -> dict:
    db: Session = SessionLocal()
    try:
        if job_id:
            mark_job_running(db, job_id)
        draft = generate_opportunity_draft(db, brief_id)
        if job_id:
            mark_job_completed(db, job_id, output_ref=str(draft.id))
        return {"draft_id": str(draft.id), "brief_id": brief_id, "version": draft.version}
    except Exception as exc:
        if job_id:
            mark_job_failed(db, job_id, str(exc))
        raise
    finally:
        db.close()
