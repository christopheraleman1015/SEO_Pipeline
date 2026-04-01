from datetime import date, datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.artifact import Artifact
from app.models.page import Page
from app.models.query_metric import QueryMetricDaily
from app.services.normalization import normalize_url
from app.utils.ids import as_uuid


def _coerce_date(value: str) -> date:
    return datetime.strptime(value.strip(), "%Y-%m-%d").date()


def _coerce_float(value: str | None) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


def _coerce_int(value: str | None) -> int:
    if value in (None, ""):
        return 0
    return int(float(value))


def get_artifact(db: Session, artifact_id: str) -> Artifact | None:
    return db.scalar(select(Artifact).where(Artifact.id == as_uuid(artifact_id)))


def replace_query_metrics_from_rows(db: Session, project_id: str, rows: list[dict]) -> int:
    project_uuid = as_uuid(project_id)
    db.execute(delete(QueryMetricDaily).where(QueryMetricDaily.project_id == project_uuid))

    page_lookup = {
        page.normalized_url: page
        for page in db.scalars(select(Page).where(Page.project_id == project_uuid)).all()
    }

    for row in rows:
        page_url = row.get("page") or row.get("url")
        normalized_url = normalize_url(page_url) if page_url else None
        _page = page_lookup.get(normalized_url) if normalized_url else None

        metric = QueryMetricDaily(
            project_id=project_uuid,
            query=row["query"].strip(),
            page_url=normalized_url,
            date=_coerce_date(row["date"]),
            clicks=_coerce_int(row.get("clicks")),
            impressions=_coerce_int(row.get("impressions")),
            ctr=_coerce_float(row.get("ctr")),
            avg_position=_coerce_float(row.get("position")) if row.get("position") else None,
        )
        db.add(metric)

    db.commit()
    return len(rows)
