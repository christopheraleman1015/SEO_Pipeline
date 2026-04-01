from collections import defaultdict

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity
from app.models.page import Page
from app.models.query_metric import QueryMetricDaily
from app.services.scoring import compute_opportunity_score
from app.utils.ids import as_uuid


def _rankability(avg_position: float | None) -> float:
    if avg_position is None:
        return 0.3
    if avg_position <= 3:
        return 0.2
    if avg_position <= 10:
        return 0.7
    if avg_position <= 20:
        return 1.0
    return 0.8


def _freshness_need(clicks: int, impressions: int, ctr: float, avg_position: float | None) -> float:
    if impressions == 0:
        return 0.0
    if avg_position and avg_position <= 5 and ctr < 0.03:
        return 0.9
    if clicks == 0 and impressions > 50:
        return 0.8
    return 0.4


def _content_gap(page: Page | None) -> float:
    if page is None:
        return 1.0
    score = 0.0
    if not page.title:
        score += 0.35
    if not page.h1:
        score += 0.25
    if page.word_count is not None and page.word_count < 300:
        score += 0.40
    return min(score, 1.0)


def _business_value(query: str) -> float:
    normalized = query.lower()
    commercial_modifiers = ("best", "pricing", "cost", "service", "software", "agency", "tool")
    return 1.0 if any(term in normalized for term in commercial_modifiers) else 0.5


def compute_project_opportunities(db: Session, project_id: str) -> dict:
    project_uuid = as_uuid(project_id)
    db.execute(delete(Opportunity).where(Opportunity.project_id == project_uuid))

    pages = {
        page.normalized_url: page
        for page in db.scalars(select(Page).where(Page.project_id == project_uuid)).all()
    }
    metrics = list(
        db.scalars(select(QueryMetricDaily).where(QueryMetricDaily.project_id == project_uuid)).all()
    )

    grouped: dict[tuple[str, str | None], list[QueryMetricDaily]] = defaultdict(list)
    for metric in metrics:
        grouped[(metric.query, metric.page_url)].append(metric)

    created = 0
    for (query, page_url), group in grouped.items():
        clicks = sum(item.clicks for item in group)
        impressions = sum(item.impressions for item in group)
        ctr = (clicks / impressions) if impressions else 0.0
        avg_position_values = [float(item.avg_position) for item in group if item.avg_position is not None]
        avg_position = (
            sum(avg_position_values) / len(avg_position_values) if avg_position_values else None
        )
        page = pages.get(page_url) if page_url else None

        business_value = _business_value(query)
        freshness_need = _freshness_need(clicks, impressions, ctr, avg_position)
        content_gap = _content_gap(page)
        rankability = _rankability(avg_position)
        traffic_potential = min(impressions / 1000, 1.0)
        ease = 0.8 if page is not None else 0.4

        score = compute_opportunity_score(
            business_value=business_value,
            traffic_potential=traffic_potential,
            rankability=rankability,
            freshness_need=freshness_need,
            content_gap=content_gap,
            ease=ease,
        )

        reason_parts = []
        if impressions > 100:
            reason_parts.append("existing search demand")
        if avg_position and avg_position > 8:
            reason_parts.append("ranking upside")
        if ctr < 0.03 and impressions > 25:
            reason_parts.append("low CTR opportunity")
        if content_gap > 0.3:
            reason_parts.append("page quality gap")
        if not reason_parts:
            reason_parts.append("baseline candidate")

        opportunity = Opportunity(
            project_id=project_uuid,
            page_id=page.id if page else None,
            keyword=query,
            normalized_url=page_url,
            clicks=clicks,
            impressions=impressions,
            ctr=ctr,
            avg_position=avg_position,
            business_value=business_value,
            freshness_need=freshness_need,
            content_gap=content_gap,
            rankability=rankability,
            score=score,
            reason=", ".join(reason_parts),
        )
        db.add(opportunity)
        created += 1

    db.commit()
    return {"project_id": project_id, "opportunities_created": created}
