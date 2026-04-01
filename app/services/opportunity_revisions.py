from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.opportunity_brief import OpportunityBrief
from app.models.opportunity_draft import OpportunityDraft
from app.models.opportunity_review import OpportunityReview
from app.services.opportunity_drafts import _build_internal_link_block, _build_intro, _render_section
from app.utils.ids import as_uuid


def _append_revision_block(content_markdown: str, review_json: dict) -> str:
    requirements = review_json.get("revision_requirements", [])
    if not requirements:
        return content_markdown

    lines = [content_markdown.strip(), "", "## Revision Notes", ""]
    for requirement in requirements:
        lines.append(f"- {requirement}")

    if any("Expand the draft" in requirement for requirement in requirements):
        lines.extend(
            [
                "",
                "## Added Detail",
                "",
                "This revised draft adds more explanatory depth, examples, and practical detail to improve readiness.",
            ]
        )

    if any("Supply proof points" in requirement for requirement in requirements):
        lines.extend(
            [
                "",
                "## Evidence To Add",
                "",
                "Include concrete examples, proof points, deliverable detail, or other supporting evidence before publishing.",
            ]
        )

    return "\n".join(lines).strip()


def revise_opportunity_draft(db: Session, opportunity_draft_id: str) -> OpportunityDraft:
    prior_draft = db.get(OpportunityDraft, as_uuid(opportunity_draft_id))
    if not prior_draft:
        raise ValueError("Opportunity draft not found")

    brief = db.get(OpportunityBrief, prior_draft.opportunity_brief_id)
    if not brief:
        raise ValueError("Opportunity brief not found")

    latest_review = db.scalar(
        select(OpportunityReview)
        .where(OpportunityReview.opportunity_draft_id == prior_draft.id)
        .order_by(desc(OpportunityReview.version))
        .limit(1)
    )
    if not latest_review:
        raise ValueError("No review found for draft")

    latest_version = db.scalar(
        select(OpportunityDraft.version)
        .where(OpportunityDraft.opportunity_brief_id == prior_draft.opportunity_brief_id)
        .order_by(desc(OpportunityDraft.version))
        .limit(1)
    )
    version = (latest_version or 0) + 1

    content = _append_revision_block(prior_draft.content_markdown, latest_review.review_json)

    # If the prior draft somehow dropped the internal link block, rebuild it from the brief.
    if "## Internal Link Sources" not in content:
        content = "\n\n".join(
            [
                _build_intro(brief.brief_json),
                *[_render_section(section, brief.brief_json) for section in brief.brief_json.get("must_cover_sections", [])],
                _build_internal_link_block(brief.brief_json),
                content,
            ]
        ).strip()

    qa_json = {
        **prior_draft.qa_json,
        "revision_requirements_applied": latest_review.review_json.get("revision_requirements", []),
        "revised_from_draft_id": str(prior_draft.id),
    }

    revised = OpportunityDraft(
        project_id=prior_draft.project_id,
        opportunity_brief_id=prior_draft.opportunity_brief_id,
        target_page_id=prior_draft.target_page_id,
        version=version,
        status="draft",
        content_markdown=content,
        qa_json=qa_json,
    )
    db.add(revised)
    db.commit()
    db.refresh(revised)
    return revised
