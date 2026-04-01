from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.services.internal_links import generate_internal_link_opportunities
from app.services.jobs import mark_job_completed, mark_job_failed, mark_job_running
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks_internal_links.compute_internal_link_opportunities")
def compute_internal_link_opportunities(project_id: str, job_id: str | None) -> dict:
    db: Session = SessionLocal()
    try:
        if job_id:
            mark_job_running(db, job_id)
        result = generate_internal_link_opportunities(db, project_id)
        if job_id:
            mark_job_completed(db, job_id)
        return result
    except Exception as exc:
        if job_id:
            mark_job_failed(db, job_id, str(exc))
        raise
    finally:
        db.close()
