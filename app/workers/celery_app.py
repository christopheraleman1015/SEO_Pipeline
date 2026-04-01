from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery("seo_agent", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_default_queue = "standard"
celery_app.conf.task_always_eager = settings.celery_task_always_eager
celery_app.conf.task_eager_propagates = True
celery_app.conf.task_routes = {
    "app.workers.tasks_audit.*": {"queue": "critical"},
    "app.workers.tasks_briefs.*": {"queue": "critical"},
    "app.workers.tasks_cluster_opportunities.*": {"queue": "standard"},
    "app.workers.tasks_clusters.*": {"queue": "standard"},
    "app.workers.tasks_internal_links.*": {"queue": "standard"},
    "app.workers.tasks_opportunity_briefs.*": {"queue": "critical"},
    "app.workers.tasks_opportunity_drafts.*": {"queue": "critical"},
    "app.workers.tasks_opportunity_publications.*": {"queue": "critical"},
    "app.workers.tasks_opportunity_revisions.*": {"queue": "critical"},
    "app.workers.tasks_opportunity_reviews.*": {"queue": "critical"},
    "app.workers.tasks_scoring.*": {"queue": "standard"},
    "app.workers.tasks_refresh.*": {"queue": "standard"},
    "app.workers.tasks_ingestion.*": {"queue": "bulk"},
}
