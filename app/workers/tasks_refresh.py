from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.services.jobs import mark_job_completed, mark_job_failed, mark_job_running
from app.services.cannibalization import detect_cannibalization_candidates
from app.services.decay import detect_decay_candidates
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks_refresh.detect_content_decay")
def detect_content_decay(project_id: str, job_id: str | None) -> dict:
    db: Session = SessionLocal()
    try:
        if job_id:
            mark_job_running(db, job_id)
        result = detect_decay_candidates(project_id)
        if job_id:
            mark_job_completed(db, job_id)
        return result
    except Exception as exc:
        if job_id:
            mark_job_failed(db, job_id, str(exc))
        raise
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks_refresh.detect_cannibalization")
def detect_cannibalization(project_id: str) -> dict:
    return detect_cannibalization_candidates(project_id)


@celery_app.task(name="app.workers.tasks_refresh.suggest_refresh_actions")
def suggest_refresh_actions(project_id: str, job_id: str | None) -> dict:
    db: Session = SessionLocal()
    try:
        if job_id:
            mark_job_running(db, job_id)
        result = {"project_id": project_id, "status": "pending"}
        if job_id:
            mark_job_completed(db, job_id)
        return result
    except Exception as exc:
        if job_id:
            mark_job_failed(db, job_id, str(exc))
        raise
    finally:
        db.close()
