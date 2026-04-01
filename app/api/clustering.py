from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.opportunity_cluster import OpportunityCluster
from app.schemas.opportunity_cluster import OpportunityClusterRead
from app.services.jobs import create_job
from app.workers.tasks_cluster_opportunities import compute_opportunity_clusters

router = APIRouter(prefix="/projects/{project_id}/cluster-opportunities", tags=["cluster-opportunities"])


@router.post("")
def enqueue_opportunity_clusters(project_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    job = create_job(db, project_id, "compute_opportunity_clusters")
    compute_opportunity_clusters.delay(str(project_id), str(job.id))
    return {"job_id": str(job.id)}


@router.get("", response_model=list[OpportunityClusterRead])
def list_opportunity_clusters(project_id: UUID, db: Session = Depends(get_db)) -> list[OpportunityCluster]:
    stmt = (
        select(OpportunityCluster)
        .where(OpportunityCluster.project_id == project_id)
        .order_by(desc(OpportunityCluster.score), desc(OpportunityCluster.impressions))
    )
    return list(db.scalars(stmt).all())
