import re
from collections import defaultdict

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.internal_link_opportunity import InternalLinkOpportunity
from app.models.opportunity_cluster import OpportunityCluster
from app.models.page import Page
from app.utils.ids import as_uuid

STOPWORDS = {
    "a",
    "an",
    "and",
    "for",
    "in",
    "of",
    "on",
    "the",
    "to",
    "with",
}


def _tokenize(text: str | None) -> set[str]:
    if not text:
        return set()
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if token and token not in STOPWORDS
    }


def generate_internal_link_opportunities(db: Session, project_id: str) -> dict:
    project_uuid = as_uuid(project_id)
    db.execute(delete(InternalLinkOpportunity).where(InternalLinkOpportunity.project_id == project_uuid))

    pages = list(db.scalars(select(Page).where(Page.project_id == project_uuid)).all())
    clusters = list(
        db.scalars(
            select(OpportunityCluster).where(OpportunityCluster.project_id == project_uuid)
        ).all()
    )

    page_tokens = {
        page.id: _tokenize(" ".join(part for part in [page.title, page.h1, page.url] if part))
        for page in pages
    }
    page_by_norm = {page.normalized_url: page for page in pages}

    created = 0
    suggestions_by_pair: dict[tuple[str, str], float] = defaultdict(float)

    for cluster in clusters:
        target_page = page_by_norm.get(cluster.normalized_url or "")
        if not target_page:
            continue

        cluster_tokens = _tokenize(" ".join([cluster.label, cluster.primary_query, cluster.query_examples]))
        anchor = cluster.primary_query

        for source_page in pages:
            if source_page.id == target_page.id:
                continue

            overlap = len(page_tokens[source_page.id] & cluster_tokens)
            if overlap == 0:
                continue

            overlap_score = min(overlap / 4, 1.0)
            target_score = float(cluster.score)
            score = round(target_score * 0.7 + overlap_score * 0.3, 4)
            pair_key = (str(source_page.id), str(target_page.id))
            if suggestions_by_pair[pair_key] >= score:
                continue

            suggestions_by_pair[pair_key] = score
            suggestion = InternalLinkOpportunity(
                project_id=project_uuid,
                source_page_id=source_page.id,
                target_page_id=target_page.id,
                cluster_id=cluster.id,
                source_url=source_page.normalized_url,
                target_url=target_page.normalized_url,
                suggested_anchor=anchor,
                overlap_score=overlap_score,
                target_score=target_score,
                score=score,
                reason="topical overlap with high-value cluster",
            )
            db.add(suggestion)
            created += 1

    db.commit()
    return {"project_id": project_id, "suggestions_created": created}
