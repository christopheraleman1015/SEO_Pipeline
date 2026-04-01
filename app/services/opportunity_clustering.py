import re
from collections import defaultdict

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity
from app.models.opportunity_cluster import OpportunityCluster
from app.utils.ids import as_uuid

STOPWORDS = {
    "a",
    "an",
    "and",
    "for",
    "how",
    "in",
    "is",
    "of",
    "on",
    "the",
    "to",
    "with",
}


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [_normalize_token(token) for token in tokens if token not in STOPWORDS]


def _normalize_token(token: str) -> str:
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def _cluster_key(keyword: str, normalized_url: str | None) -> tuple[str | None, str]:
    tokens = _tokenize(keyword)
    head = " ".join(tokens[:3]) if tokens else keyword.lower()
    return normalized_url, head


def build_opportunity_clusters(db: Session, project_id: str) -> dict:
    project_uuid = as_uuid(project_id)
    db.execute(delete(OpportunityCluster).where(OpportunityCluster.project_id == project_uuid))

    opportunities = list(
        db.scalars(select(Opportunity).where(Opportunity.project_id == project_uuid)).all()
    )

    grouped: dict[tuple[str | None, str], list[Opportunity]] = defaultdict(list)
    for opportunity in opportunities:
        grouped[_cluster_key(opportunity.keyword, opportunity.normalized_url)].append(opportunity)

    created = 0
    for (normalized_url, label), items in grouped.items():
        impressions = sum(item.impressions for item in items)
        clicks = sum(item.clicks for item in items)
        ctr = (clicks / impressions) if impressions else 0.0
        avg_positions = [float(item.avg_position) for item in items if item.avg_position is not None]
        avg_position = sum(avg_positions) / len(avg_positions) if avg_positions else None
        top_item = max(items, key=lambda item: (float(item.score), item.impressions))
        examples = ", ".join(item.keyword for item in sorted(items, key=lambda item: item.impressions, reverse=True)[:3])

        cluster = OpportunityCluster(
            project_id=project_uuid,
            page_id=top_item.page_id,
            label=label,
            normalized_url=normalized_url,
            query_count=len(items),
            clicks=clicks,
            impressions=impressions,
            ctr=ctr,
            avg_position=avg_position,
            score=max(float(item.score) for item in items),
            primary_query=top_item.keyword,
            query_examples=examples,
            reason=top_item.reason,
        )
        db.add(cluster)
        created += 1

    db.commit()
    return {"project_id": project_id, "clusters_created": created}
