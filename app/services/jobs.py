from uuid import UUID

from sqlalchemy.orm import Session

from app.enums import JobStatus
from app.models.job import Job
from app.utils.ids import as_uuid
from app.utils.time import utc_now


def create_job(
    db: Session,
    project_id: UUID | str,
    job_type: str,
    payload: dict | None = None,
    priority: int = 50,
) -> Job:
    job = Job(
        project_id=as_uuid(project_id),
        job_type=job_type,
        status=JobStatus.QUEUED.value,
        priority=priority,
        payload=payload or {},
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def mark_job_running(db: Session, job_id: UUID | str) -> Job | None:
    job = db.get(Job, as_uuid(job_id))
    if not job:
        return None
    job.status = JobStatus.RUNNING.value
    job.started_at = utc_now()
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def mark_job_completed(db: Session, job_id: UUID | str, output_ref: str | None = None) -> Job | None:
    job = db.get(Job, as_uuid(job_id))
    if not job:
        return None
    job.status = JobStatus.COMPLETED.value
    job.output_ref = output_ref
    if not job.started_at:
        job.started_at = utc_now()
    job.finished_at = utc_now()
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def mark_job_failed(db: Session, job_id: UUID | str, error_message: str) -> Job | None:
    job = db.get(Job, as_uuid(job_id))
    if not job:
        return None
    job.status = JobStatus.FAILED.value
    job.error_message = error_message
    if not job.started_at:
        job.started_at = utc_now()
    job.finished_at = utc_now()
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
