from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.project import Project
from app.schemas.ingestion import ArtifactUploadResponse
from app.services.artifacts import create_artifact_record
from app.services.jobs import create_job
from app.workers.tasks_ingestion import import_crawl_csv, import_ga4, import_gsc, import_keywords

router = APIRouter(prefix="/projects/{project_id}/ingest", tags=["ingestion"])


@router.post("/gsc")
async def enqueue_gsc(
    project_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ArtifactUploadResponse:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    content = await file.read()
    artifact = create_artifact_record(
        db=db,
        project_id=project_id,
        artifact_type="gsc",
        source_name=file.filename or "gsc.csv",
        content=content,
    )
    job = create_job(db, project_id, "import_gsc", payload={"artifact_id": str(artifact.id)})
    import_gsc.delay(str(project_id), str(job.id), str(artifact.id), None, None)
    return ArtifactUploadResponse(artifact_id=artifact.id, job_id=str(job.id))


@router.post("/ga4")
def enqueue_ga4(project_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    job = create_job(db, project_id, "import_ga4")
    import_ga4.delay(str(project_id), str(job.id), None, None)
    return {"job_id": str(job.id)}


@router.post("/crawl", response_model=ArtifactUploadResponse)
async def enqueue_crawl(
    project_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ArtifactUploadResponse:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    content = await file.read()
    artifact = create_artifact_record(
        db=db,
        project_id=project_id,
        artifact_type="crawls",
        source_name=file.filename or "crawl.csv",
        content=content,
    )
    job = create_job(db, project_id, "import_crawl_csv", payload={"artifact_id": str(artifact.id)})
    import_crawl_csv.delay(str(project_id), str(job.id), str(artifact.id))
    return ArtifactUploadResponse(artifact_id=artifact.id, job_id=str(job.id))


@router.post("/keywords")
def enqueue_keywords(project_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    job = create_job(db, project_id, "import_keywords")
    import_keywords.delay(str(project_id), str(job.id), None)
    return {"job_id": str(job.id)}
