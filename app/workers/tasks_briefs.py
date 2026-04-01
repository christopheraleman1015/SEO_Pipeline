from app.llm.tasks import run_brief_generation
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks_briefs.generate_content_brief")
def generate_content_brief(cluster_id: str, job_id: str | None) -> dict:
    payload = {"cluster_id": cluster_id}
    return run_brief_generation(payload)


@celery_app.task(name="app.workers.tasks_briefs.run_brief_quality_checks")
def run_brief_quality_checks(brief_id: str) -> dict:
    return {"brief_id": brief_id, "status": "pending"}
