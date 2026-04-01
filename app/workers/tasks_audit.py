from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.services.jobs import mark_job_completed, mark_job_failed, mark_job_running
from app.services.technical_audit import run_audit_rules
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks_audit.run_technical_audit")
def run_technical_audit(project_id: str, job_id: str | None) -> dict:
    db: Session = SessionLocal()
    try:
        if job_id:
            mark_job_running(db, job_id)
        result = run_audit_rules(db, project_id)
        if job_id:
            mark_job_completed(db, job_id)
        return result
    except Exception as exc:
        if job_id:
            mark_job_failed(db, job_id, str(exc))
        raise
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks_audit.detect_orphan_pages")
def detect_orphan_pages(project_id: str) -> dict:
    return {"project_id": project_id, "orphans": 0}


@celery_app.task(name="app.workers.tasks_audit.detect_duplicate_clusters")
def detect_duplicate_clusters(project_id: str) -> dict:
    return {"project_id": project_id, "duplicates": 0}
