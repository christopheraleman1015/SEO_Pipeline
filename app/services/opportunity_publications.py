from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.connectors.cms import publish_update
from app.models.opportunity_brief import OpportunityBrief
from app.models.opportunity_draft import OpportunityDraft
from app.models.opportunity_publication import OpportunityPublication
from app.models.project_publisher_config import ProjectPublisherConfig
from app.models.opportunity_review import OpportunityReview
from app.models.page import Page
from app.utils.ids import as_uuid


def _latest_review(db: Session, draft_id: str) -> OpportunityReview | None:
    return db.scalar(
        select(OpportunityReview)
        .where(OpportunityReview.opportunity_draft_id == as_uuid(draft_id))
        .order_by(desc(OpportunityReview.version))
        .limit(1)
    )


def _latest_publication(db: Session, draft_id: str) -> OpportunityPublication | None:
    return db.scalar(
        select(OpportunityPublication)
        .where(OpportunityPublication.opportunity_draft_id == as_uuid(draft_id))
        .order_by(desc(OpportunityPublication.created_at))
        .limit(1)
    )


def approve_opportunity_draft_for_publish(db: Session, draft_id: str) -> OpportunityPublication:
    draft = db.get(OpportunityDraft, as_uuid(draft_id))
    if not draft:
        raise ValueError("Opportunity draft not found")

    review = _latest_review(db, draft_id)
    if not review or not review.review_json.get("publish_ready"):
        raise ValueError("Draft is not publish-ready")

    publication = _latest_publication(db, draft_id)
    if publication is None:
        publication = OpportunityPublication(
            project_id=draft.project_id,
            opportunity_draft_id=draft.id,
            approved_for_publish=True,
            published=False,
            target_url=None,
            publish_result_json={"status": "approved"},
        )
        db.add(publication)
    else:
        publication.approved_for_publish = True
        publication.publish_result_json = {
            **publication.publish_result_json,
            "status": "approved",
        }
        db.add(publication)

    db.commit()
    db.refresh(publication)
    return publication


def publish_approved_draft(db: Session, draft_id: str) -> OpportunityPublication:
    draft = db.get(OpportunityDraft, as_uuid(draft_id))
    if not draft:
        raise ValueError("Opportunity draft not found")

    review = _latest_review(db, draft_id)
    if not review or not review.review_json.get("publish_ready"):
        raise ValueError("Draft failed publish gate")

    publication = _latest_publication(db, draft_id)
    if not publication or not publication.approved_for_publish:
        raise ValueError("Draft has not been explicitly approved for publish")

    brief = db.get(OpportunityBrief, draft.opportunity_brief_id)
    page = db.get(Page, draft.target_page_id) if draft.target_page_id else None
    publisher_config = db.scalar(
        select(ProjectPublisherConfig).where(ProjectPublisherConfig.project_id == draft.project_id).limit(1)
    )
    target_url = page.normalized_url if page else brief.brief_json.get("target_url") if brief else None

    connector_result = publish_update(
        str(draft.project_id),
        {
            "target_url": target_url,
            "content_markdown": draft.content_markdown,
            "draft_id": str(draft.id),
            "title": brief.brief_json.get("title_options", [None])[0] if brief else None,
        },
        provider=publisher_config.provider if publisher_config else "generic_rest",
        mode=publisher_config.mode if publisher_config else "draft",
        config=publisher_config.config_json if publisher_config else {},
    )

    publication.published = True
    publication.target_url = target_url
    publication.publish_result_json = {
        **publication.publish_result_json,
        "status": "published",
        "connector_result": connector_result,
    }
    db.add(publication)
    db.commit()
    db.refresh(publication)
    return publication
