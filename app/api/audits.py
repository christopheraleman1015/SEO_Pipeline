from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.issue import Issue
from app.schemas.issue import IssueRead
from app.services.jobs import create_job
from app.workers.tasks_audit import run_technical_audit

router = APIRouter(prefix="/projects/{project_id}", tags=["audits"])


@router.post("/audit/technical")
def enqueue_technical_audit(project_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    job = create_job(db, project_id, "run_technical_audit")
    run_technical_audit.delay(str(project_id), str(job.id))
    return {"job_id": str(job.id)}


@router.get("/issues", response_model=list[IssueRead])
def list_issues(project_id: UUID, db: Session = Depends(get_db)) -> list[Issue]:
    return list(db.scalars(select(Issue).where(Issue.project_id == project_id)).all())


@router.get("/issues/summary")
def issue_summary(project_id: UUID, db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(Issue.severity, func.count(Issue.id))
        .where(Issue.project_id == project_id)
        .group_by(Issue.severity)
    ).all()
    return {
        "project_id": str(project_id),
        "counts_by_severity": {severity: count for severity, count in rows},
        "total": sum(count for _, count in rows),
    }
