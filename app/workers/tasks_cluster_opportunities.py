from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.services.jobs import mark_job_completed, mark_job_failed, mark_job_running
from app.services.opportunity_clustering import build_opportunity_clusters
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks_cluster_opportunities.compute_opportunity_clusters")
def compute_opportunity_clusters(project_id: str, job_id: str | None) -> dict:
    db: Session = SessionLocal()
    try:
        if job_id:
            mark_job_running(db, job_id)
        result = build_opportunity_clusters(db, project_id)
        if job_id:
            mark_job_completed(db, job_id)
        return result
    except Exception as exc:
        if job_id:
            mark_job_failed(db, job_id, str(exc))
        raise
    finally:
        db.close()
