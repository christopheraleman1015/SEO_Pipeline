from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.internal_link_opportunity import InternalLinkOpportunity
from app.models.opportunity import Opportunity
from app.models.opportunity_brief import OpportunityBrief
from app.models.opportunity_cluster import OpportunityCluster
from app.models.opportunity_draft import OpportunityDraft
from app.models.opportunity_publication import OpportunityPublication
from app.models.opportunity_review import OpportunityReview
from app.schemas.internal_link_opportunity import InternalLinkOpportunityRead
from app.schemas.opportunity import OpportunityRead
from app.schemas.opportunity_brief import OpportunityBriefRead
from app.schemas.opportunity_cluster import OpportunityClusterRead
from app.schemas.opportunity_draft import OpportunityDraftRead
from app.schemas.opportunity_publication import OpportunityPublicationRead
from app.schemas.opportunity_review import OpportunityReviewRead

router = APIRouter(prefix="/projects/{project_id}/workflow", tags=["workflow"])


@router.get("/overview")
def get_workflow_overview(project_id: UUID, db: Session = Depends(get_db)) -> dict:
    return {
        "project_id": str(project_id),
        "opportunities": db.scalar(
            select(func.count(Opportunity.id)).where(Opportunity.project_id == project_id)
        )
        or 0,
        "clusters": db.scalar(
            select(func.count(OpportunityCluster.id)).where(OpportunityCluster.project_id == project_id)
        )
        or 0,
        "briefs": db.scalar(
            select(func.count(OpportunityBrief.id)).where(OpportunityBrief.project_id == project_id)
        )
        or 0,
        "drafts": db.scalar(
            select(func.count(OpportunityDraft.id)).where(OpportunityDraft.project_id == project_id)
        )
        or 0,
        "reviews": db.scalar(
            select(func.count(OpportunityReview.id))
            .join(OpportunityDraft, OpportunityDraft.id == OpportunityReview.opportunity_draft_id)
            .where(OpportunityDraft.project_id == project_id)
        )
        or 0,
        "internal_link_opportunities": db.scalar(
            select(func.count(InternalLinkOpportunity.id)).where(
                InternalLinkOpportunity.project_id == project_id
            )
        )
        or 0,
        "publications": db.scalar(
            select(func.count(OpportunityPublication.id)).where(
                OpportunityPublication.project_id == project_id
            )
        )
        or 0,
    }


@router.get("/opportunities", response_model=list[OpportunityRead])
def list_project_opportunities(project_id: UUID, db: Session = Depends(get_db)) -> list[Opportunity]:
    stmt = (
        select(Opportunity)
        .where(Opportunity.project_id == project_id)
        .order_by(desc(Opportunity.score), desc(Opportunity.impressions))
    )
    return list(db.scalars(stmt).all())


@router.get("/clusters", response_model=list[OpportunityClusterRead])
def list_project_clusters(project_id: UUID, db: Session = Depends(get_db)) -> list[OpportunityCluster]:
    stmt = (
        select(OpportunityCluster)
        .where(OpportunityCluster.project_id == project_id)
        .order_by(desc(OpportunityCluster.score), desc(OpportunityCluster.impressions))
    )
    return list(db.scalars(stmt).all())


@router.get("/briefs", response_model=list[OpportunityBriefRead])
def list_project_briefs(project_id: UUID, db: Session = Depends(get_db)) -> list[OpportunityBrief]:
    stmt = (
        select(OpportunityBrief)
        .where(OpportunityBrief.project_id == project_id)
        .order_by(desc(OpportunityBrief.created_at))
    )
    return list(db.scalars(stmt).all())


@router.get("/drafts", response_model=list[OpportunityDraftRead])
def list_project_drafts(project_id: UUID, db: Session = Depends(get_db)) -> list[OpportunityDraft]:
    stmt = (
        select(OpportunityDraft)
        .where(OpportunityDraft.project_id == project_id)
        .order_by(desc(OpportunityDraft.created_at))
    )
    return list(db.scalars(stmt).all())


@router.get("/reviews", response_model=list[OpportunityReviewRead])
def list_project_reviews(project_id: UUID, db: Session = Depends(get_db)) -> list[OpportunityReview]:
    stmt = (
        select(OpportunityReview)
        .join(OpportunityDraft, OpportunityDraft.id == OpportunityReview.opportunity_draft_id)
        .where(OpportunityDraft.project_id == project_id)
        .order_by(desc(OpportunityReview.created_at))
    )
    return list(db.scalars(stmt).all())


@router.get("/internal-links", response_model=list[InternalLinkOpportunityRead])
def list_project_internal_links(
    project_id: UUID, db: Session = Depends(get_db)
) -> list[InternalLinkOpportunity]:
    stmt = (
        select(InternalLinkOpportunity)
        .where(InternalLinkOpportunity.project_id == project_id)
        .order_by(desc(InternalLinkOpportunity.score))
    )
    return list(db.scalars(stmt).all())


@router.get("/publications", response_model=list[OpportunityPublicationRead])
def list_project_publications(
    project_id: UUID, db: Session = Depends(get_db)
) -> list[OpportunityPublication]:
    stmt = (
        select(OpportunityPublication)
        .where(OpportunityPublication.project_id == project_id)
        .order_by(desc(OpportunityPublication.created_at))
    )
    return list(db.scalars(stmt).all())
