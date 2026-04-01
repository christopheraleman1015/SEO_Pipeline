from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.internal_link_opportunity import InternalLinkOpportunity
from app.models.opportunity_brief import OpportunityBrief
from app.models.opportunity_cluster import OpportunityCluster
from app.models.page import Page
from app.utils.ids import as_uuid


def _build_sections(cluster: OpportunityCluster, page: Page | None) -> list[str]:
    sections = ["Direct answer / offer overview", "Primary benefits or outcomes", "FAQs"]
    label = cluster.label.lower()

    if "pricing" in label or "cost" in label:
        sections.insert(1, "Pricing factors")
        sections.insert(2, "Package or service comparison")
    if "checklist" in label:
        sections.insert(1, "Step-by-step checklist")
    if "service" in label or "agency" in label:
        sections.insert(1, "What is included")
        sections.insert(2, "Who this is for")
    if page and page.word_count is not None and page.word_count < 300:
        sections.append("Expanded trust and proof section")

    seen = set()
    ordered = []
    for section in sections:
        if section not in seen:
            ordered.append(section)
            seen.add(section)
    return ordered


def _build_differentiator(cluster: OpportunityCluster, page: Page | None) -> str:
    if page and page.word_count is not None and page.word_count < 300:
        return "Expand beyond current thin page with proof, examples, and a stronger conversion section."
    if "pricing" in cluster.label.lower() or "cost" in cluster.label.lower():
        return "Add concrete pricing structure, examples, and buyer decision guidance."
    if "service" in cluster.label.lower():
        return "Show deliverables, process, and who the service is best for."
    return "Cover the topic more directly than the current page and add practical examples."


def generate_opportunity_brief(db: Session, opportunity_cluster_id: str) -> OpportunityBrief:
    cluster = db.get(OpportunityCluster, as_uuid(opportunity_cluster_id))
    if not cluster:
        raise ValueError("Opportunity cluster not found")

    target_page = db.get(Page, cluster.page_id) if cluster.page_id else None
    latest_version = db.scalar(
        select(OpportunityBrief.version)
        .where(OpportunityBrief.opportunity_cluster_id == cluster.id)
        .order_by(desc(OpportunityBrief.version))
        .limit(1)
    )
    version = (latest_version or 0) + 1

    internal_links = list(
        db.scalars(
            select(InternalLinkOpportunity)
            .where(InternalLinkOpportunity.cluster_id == cluster.id)
            .order_by(desc(InternalLinkOpportunity.score))
            .limit(5)
        ).all()
    )

    brief_json = {
        "target_query": cluster.primary_query,
        "cluster_label": cluster.label,
        "page_goal": "Improve rankings and conversions for this search cluster.",
        "target_url": cluster.normalized_url,
        "audience": "Searcher evaluating options or seeking a direct solution.",
        "title_options": [
            cluster.primary_query.title(),
            f"{cluster.primary_query.title()} | {cluster.label.title()}",
        ],
        "h1_options": [
            cluster.primary_query.title(),
            cluster.label.title(),
        ],
        "must_cover_sections": _build_sections(cluster, target_page),
        "internal_link_sources": [
            {
                "source_url": item.source_url,
                "anchor": item.suggested_anchor,
                "score": float(item.score),
            }
            for item in internal_links
        ],
        "schema_types": ["WebPage", "FAQPage"] if "pricing" not in cluster.label else ["WebPage"],
        "differentiator": _build_differentiator(cluster, target_page),
        "evidence_required": [
            "Specific examples or proof points",
            "Clear service/process details if applicable",
        ],
        "risks": [
            "Current target page may be too thin",
            "SERP intent may need tighter matching if CTR remains low",
        ],
    }

    brief = OpportunityBrief(
        project_id=cluster.project_id,
        opportunity_cluster_id=cluster.id,
        target_page_id=cluster.page_id,
        version=version,
        status="draft",
        brief_json=brief_json,
    )
    db.add(brief)
    db.commit()
    db.refresh(brief)
    return brief
