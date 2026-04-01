from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.opportunity_brief import OpportunityBrief
from app.models.opportunity_draft import OpportunityDraft
from app.models.page import Page
from app.utils.ids import as_uuid


def _render_section(section: str, brief_json: dict) -> str:
    query = brief_json["target_query"]
    if section == "Direct answer / offer overview":
        return (
            f"## {section}\n\n"
            f"{query.title()} should directly explain what the visitor gets, who it is for, "
            "and why this page is the right next step.\n"
        )
    if section == "Pricing factors":
        return (
            f"## {section}\n\n"
            "Break down the main variables that change pricing, such as scope, complexity, and deliverables.\n"
        )
    if section == "Package or service comparison":
        return (
            f"## {section}\n\n"
            "Compare entry, standard, and advanced options so the user can self-select quickly.\n"
        )
    if section == "What is included":
        return (
            f"## {section}\n\n"
            "List deliverables, timeline, and what the engagement actually covers.\n"
        )
    if section == "Who this is for":
        return (
            f"## {section}\n\n"
            "Clarify ideal fit, common use cases, and who should consider a different solution.\n"
        )
    if section == "Expanded trust and proof section":
        return (
            f"## {section}\n\n"
            "Add examples, proof points, process detail, and concrete outputs to improve trust.\n"
        )
    if section == "Primary benefits or outcomes":
        return (
            f"## {section}\n\n"
            "Focus on the measurable outcomes the user cares about rather than generic feature language.\n"
        )
    if section == "FAQs":
        return (
            f"## {section}\n\n"
            "- What does this include?\n"
            "- How long does it take?\n"
            "- What affects cost or scope?\n"
        )
    return f"## {section}\n\nAdd a focused section for {section.lower()}.\n"


def _build_intro(brief_json: dict) -> str:
    return (
        f"# {brief_json['h1_options'][0]}\n\n"
        f"{brief_json['target_query'].title()} should satisfy the searcher quickly, "
        "show what makes the offer useful, and move them toward the right next action.\n"
    )


def _build_internal_link_block(brief_json: dict) -> str:
    links = brief_json.get("internal_link_sources", [])
    if not links:
        return ""
    lines = ["## Internal Link Sources", ""]
    for link in links:
        lines.append(f"- Add a contextual link from {link['source_url']} using anchor `{link['anchor']}`.")
    lines.append("")
    return "\n".join(lines)


def _build_qa_json(brief_json: dict, page: Page | None) -> dict:
    sections = brief_json.get("must_cover_sections", [])
    return {
        "section_count": len(sections),
        "has_internal_link_sources": bool(brief_json.get("internal_link_sources")),
        "target_page_is_thin": bool(page and page.word_count is not None and page.word_count < 300),
        "risk_count": len(brief_json.get("risks", [])),
        "evidence_items": brief_json.get("evidence_required", []),
    }


def generate_opportunity_draft(db: Session, opportunity_brief_id: str) -> OpportunityDraft:
    brief = db.get(OpportunityBrief, as_uuid(opportunity_brief_id))
    if not brief:
        raise ValueError("Opportunity brief not found")

    page = db.get(Page, brief.target_page_id) if brief.target_page_id else None
    latest_version = db.scalar(
        select(OpportunityDraft.version)
        .where(OpportunityDraft.opportunity_brief_id == brief.id)
        .order_by(desc(OpportunityDraft.version))
        .limit(1)
    )
    version = (latest_version or 0) + 1

    brief_json = brief.brief_json
    sections = [_render_section(section, brief_json) for section in brief_json.get("must_cover_sections", [])]
    body = "\n".join([_build_intro(brief_json), *sections, _build_internal_link_block(brief_json)]).strip()

    draft = OpportunityDraft(
        project_id=brief.project_id,
        opportunity_brief_id=brief.id,
        target_page_id=brief.target_page_id,
        version=version,
        status="draft",
        content_markdown=body,
        qa_json=_build_qa_json(brief_json, page),
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft
