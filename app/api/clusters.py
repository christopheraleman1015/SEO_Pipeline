from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.cluster import Cluster
from app.schemas.cluster import ClusterRead
from app.services.jobs import create_job
from app.workers.tasks_clusters import build_keyword_clusters
from app.workers.tasks_serp import analyze_serp_cluster

router = APIRouter(tags=["clusters"])


@router.post("/projects/{project_id}/clusters/build")
def enqueue_cluster_build(project_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    job = create_job(db, project_id, "build_keyword_clusters")
    build_keyword_clusters.delay(str(project_id), str(job.id))
    return {"job_id": str(job.id)}


@router.get("/projects/{project_id}/clusters", response_model=list[ClusterRead])
def list_clusters(project_id: UUID, db: Session = Depends(get_db)) -> list[Cluster]:
    return list(db.scalars(select(Cluster).where(Cluster.project_id == project_id)).all())


@router.get("/clusters/{cluster_id}", response_model=ClusterRead)
def get_cluster(cluster_id: UUID, db: Session = Depends(get_db)) -> Cluster:
    cluster = db.get(Cluster, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster


@router.post("/clusters/{cluster_id}/analyze-serp")
def enqueue_serp_analysis(cluster_id: UUID) -> dict[str, str]:
    task = analyze_serp_cluster.delay(str(cluster_id), None)
    return {"job_id": task.id}
