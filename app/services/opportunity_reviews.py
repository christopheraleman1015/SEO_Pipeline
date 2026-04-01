from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.opportunity_brief import OpportunityBrief
from app.models.opportunity_draft import OpportunityDraft
from app.models.opportunity_evidence import OpportunityEvidence
from app.models.opportunity_review import OpportunityReview
from app.utils.ids import as_uuid


def _check_required_sections(draft_markdown: str, required_sections: list[str]) -> list[str]:
    missing = []
    lower_markdown = draft_markdown.lower()
    for section in required_sections:
        if f"## {section}".lower() not in lower_markdown:
            missing.append(section)
    return missing


def _count_words(text: str) -> int:
    return len([token for token in text.split() if token.strip()])


def _normalize_text(value: str) -> str:
    return value.lower().strip()


def _resolve_evidence_items(
    db: Session, brief_id: str, evidence_items: list[str]
) -> tuple[list[str], list[str]]:
    evidence_records = list(
        db.scalars(
            select(OpportunityEvidence).where(OpportunityEvidence.opportunity_brief_id == as_uuid(brief_id))
        ).all()
    )
    corpus = " ".join(
        filter(
            None,
            [
                *(item.title for item in evidence_records),
                *(item.content_text or "" for item in evidence_records),
            ],
        )
    ).lower()

    satisfied: list[str] = []
    missing: list[str] = []
    for item in evidence_items:
        normalized = _normalize_text(item)
        keywords = [token for token in normalized.replace("/", " ").split() if len(token) > 3]
        if keywords and any(keyword in corpus for keyword in keywords):
            satisfied.append(item)
        else:
            missing.append(item)
    return satisfied, missing


def review_opportunity_draft(db: Session, opportunity_draft_id: str) -> OpportunityReview:
    draft = db.get(OpportunityDraft, as_uuid(opportunity_draft_id))
    if not draft:
        raise ValueError("Opportunity draft not found")

    brief = db.get(OpportunityBrief, draft.opportunity_brief_id)
    if not brief:
        raise ValueError("Opportunity brief not found")

    latest_version = db.scalar(
        select(OpportunityReview.version)
        .where(OpportunityReview.opportunity_draft_id == draft.id)
        .order_by(desc(OpportunityReview.version))
        .limit(1)
    )
    version = (latest_version or 0) + 1

    required_sections = brief.brief_json.get("must_cover_sections", [])
    missing_sections = _check_required_sections(draft.content_markdown, required_sections)
    word_count = _count_words(draft.content_markdown)
    evidence_items = draft.qa_json.get("evidence_items", [])
    satisfied_evidence, missing_evidence = _resolve_evidence_items(db, str(brief.id), evidence_items)
    internal_links_present = draft.qa_json.get("has_internal_link_sources", False)

    findings = []
    revision_requirements = []

    if missing_sections:
        findings.append("Missing required sections")
        revision_requirements.append(
            f"Add all required sections: {', '.join(missing_sections)}."
        )

    if word_count < 250:
        findings.append("Draft is too short")
        revision_requirements.append("Expand the draft with meaningful detail and examples.")

    if not internal_links_present:
        findings.append("No internal link guidance included")
        revision_requirements.append("Add internal link source guidance to the draft.")

    if missing_evidence:
        findings.append("Evidence still required before publishing")
        revision_requirements.append(
            "Supply proof points or examples for: " + ", ".join(missing_evidence) + "."
        )

    if "TODO" in draft.content_markdown:
        findings.append("Placeholder content detected")
        revision_requirements.append("Replace placeholders with final content.")

    publish_ready = len(findings) == 0
    review_json = {
        "publish_ready": publish_ready,
        "findings": findings,
        "revision_requirements": revision_requirements,
        "word_count": word_count,
        "missing_sections": missing_sections,
        "evidence_items": evidence_items,
        "satisfied_evidence_items": satisfied_evidence,
        "missing_evidence_items": missing_evidence,
    }

    review = OpportunityReview(
        project_id=draft.project_id,
        opportunity_draft_id=draft.id,
        version=version,
        status="reviewed",
        review_json=review_json,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
