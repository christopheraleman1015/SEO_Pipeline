from app.connectors.serp import fetch_serp_snapshot
from app.llm.tasks import run_serp_synthesis
from app.services.serp_features import summarize_serp_snapshot
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks_serp.fetch_serp_snapshot")
def fetch_serp_snapshot_task(cluster_id: str) -> dict:
    return fetch_serp_snapshot(cluster_id)


@celery_app.task(name="app.workers.tasks_serp.analyze_serp_cluster")
def analyze_serp_cluster(cluster_id: str, job_id: str | None) -> dict:
    snapshot = fetch_serp_snapshot(cluster_id)
    summary = summarize_serp_snapshot(snapshot)
    return run_serp_synthesis(summary)
