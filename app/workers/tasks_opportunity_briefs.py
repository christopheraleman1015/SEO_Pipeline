from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.services.jobs import mark_job_completed, mark_job_failed, mark_job_running
from app.services.opportunity_briefs import generate_opportunity_brief
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks_opportunity_briefs.generate_cluster_brief")
def generate_cluster_brief(cluster_id: str, job_id: str | None) -> dict:
    db: Session = SessionLocal()
    try:
        if job_id:
            mark_job_running(db, job_id)
        brief = generate_opportunity_brief(db, cluster_id)
        if job_id:
            mark_job_completed(db, job_id, output_ref=str(brief.id))
        return {"brief_id": str(brief.id), "cluster_id": cluster_id, "version": brief.version}
    except Exception as exc:
        if job_id:
            mark_job_failed(db, job_id, str(exc))
        raise
    finally:
        db.close()
