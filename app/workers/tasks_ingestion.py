from sqlalchemy.orm import Session

from app.connectors.crawler import import_crawl_export
from app.connectors.gsc_csv import import_gsc_csv
from app.connectors.ga4 import import_ga4_data
from app.connectors.gsc import import_gsc_data
from app.db import SessionLocal
from app.services.crawl_ingestion import get_artifact, replace_project_pages_from_crawl
from app.services.gsc_ingestion import (
    get_artifact as get_gsc_artifact,
    replace_query_metrics_from_rows,
)
from app.services.jobs import mark_job_completed, mark_job_failed, mark_job_running
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks_ingestion.import_gsc")
def import_gsc(
    project_id: str, job_id: str | None, artifact_id: str | None, date_from: str | None, date_to: str | None
) -> dict:
    db: Session = SessionLocal()
    try:
        if job_id:
            mark_job_running(db, job_id)
        if artifact_id:
            artifact = get_gsc_artifact(db, artifact_id)
            if not artifact:
                if job_id:
                    mark_job_failed(db, job_id, "artifact_not_found")
                return {
                    "project_id": project_id,
                    "artifact_id": artifact_id,
                    "status": "artifact_not_found",
                }
            parsed = import_gsc_csv(artifact.storage_path)
            ingested = replace_query_metrics_from_rows(db, project_id, parsed["rows"])
            result = {
                "project_id": project_id,
                "artifact_id": artifact_id,
                "rows_ingested": ingested,
                "source_path": artifact.storage_path,
            }
        else:
            result = import_gsc_data(project_id, date_from, date_to)
        if job_id:
            mark_job_completed(db, job_id)
        return result
    except Exception as exc:
        if job_id:
            mark_job_failed(db, job_id, str(exc))
        raise
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks_ingestion.import_ga4")
def import_ga4(project_id: str, job_id: str | None, date_from: str | None, date_to: str | None) -> dict:
    db: Session = SessionLocal()
    try:
        if job_id:
            mark_job_running(db, job_id)
        result = import_ga4_data(project_id, date_from, date_to)
        if job_id:
            mark_job_completed(db, job_id)
        return result
    except Exception as exc:
        if job_id:
            mark_job_failed(db, job_id, str(exc))
        raise
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks_ingestion.import_crawl_csv")
def import_crawl_csv(project_id: str, job_id: str | None, artifact_id: str | None) -> dict:
    db: Session = SessionLocal()
    if artifact_id is None:
        return {"project_id": project_id, "status": "missing_artifact"}
    try:
        if job_id:
            mark_job_running(db, job_id)
        artifact = get_artifact(db, artifact_id)
        if not artifact:
            if job_id:
                mark_job_failed(db, job_id, "artifact_not_found")
            return {"project_id": project_id, "artifact_id": artifact_id, "status": "artifact_not_found"}

        parsed = import_crawl_export(project_id, artifact.storage_path)
        ingested = replace_project_pages_from_crawl(db, project_id, parsed["pages"])
        if job_id:
            mark_job_completed(db, job_id, output_ref=artifact.storage_path)
        return {
            "project_id": project_id,
            "artifact_id": artifact_id,
            "pages_ingested": ingested,
            "source_path": artifact.storage_path,
        }
    except Exception as exc:
        if job_id:
            mark_job_failed(db, job_id, str(exc))
        raise
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks_ingestion.import_keywords")
def import_keywords(project_id: str, job_id: str | None, artifact_id: str | None) -> dict:
    db: Session = SessionLocal()
    try:
        if job_id:
            mark_job_running(db, job_id)
        result = {"project_id": project_id, "artifact_id": artifact_id, "keywords": 0}
        if job_id:
            mark_job_completed(db, job_id)
        return result
    except Exception as exc:
        if job_id:
            mark_job_failed(db, job_id, str(exc))
        raise
    finally:
        db.close()
