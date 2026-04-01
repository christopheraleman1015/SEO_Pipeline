from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.opportunity_brief import OpportunityBrief
from app.models.opportunity_cluster import OpportunityCluster
from app.schemas.opportunity_brief import OpportunityBriefRead
from app.services.jobs import create_job
from app.workers.tasks_opportunity_briefs import generate_cluster_brief

router = APIRouter(tags=["opportunity-briefs"])


@router.post("/opportunity-clusters/{cluster_id}/briefs")
def enqueue_opportunity_brief(cluster_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    target_cluster = db.get(OpportunityCluster, cluster_id)
    if not target_cluster:
        raise HTTPException(status_code=404, detail="Opportunity cluster not found")

    job = create_job(
        db,
        target_cluster.project_id,
        "generate_opportunity_brief",
        payload={"cluster_id": str(cluster_id)},
    )
    generate_cluster_brief.delay(str(cluster_id), str(job.id))
    return {"job_id": str(job.id)}


@router.get("/opportunity-clusters/{cluster_id}/briefs/latest", response_model=OpportunityBriefRead)
def get_latest_opportunity_brief(cluster_id: UUID, db: Session = Depends(get_db)) -> OpportunityBrief:
    brief = db.scalar(
        select(OpportunityBrief)
        .where(OpportunityBrief.opportunity_cluster_id == cluster_id)
        .order_by(desc(OpportunityBrief.version))
        .limit(1)
    )
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    return brief
