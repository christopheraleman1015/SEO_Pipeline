from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.artifact import Artifact
from app.models.page import Page
from app.services.normalization import normalize_url
from app.utils.ids import as_uuid


def _coerce_int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def _coerce_bool_from_indexability(indexability: str | None, meta_robots: str | None) -> bool | None:
    if indexability:
        normalized = indexability.strip().lower()
        if "indexable" == normalized:
            return True
        if "non-indexable" == normalized:
            return False
    if meta_robots:
        return "noindex" not in meta_robots.lower()
    return None


def replace_project_pages_from_crawl(db: Session, project_id: str, parsed_rows: list[dict]) -> int:
    project_uuid = as_uuid(project_id)
    db.execute(delete(Page).where(Page.project_id == project_uuid))

    for row in parsed_rows:
        meta_robots = row.get("meta_robots")
        page = Page(
            project_id=project_uuid,
            url=row["url"],
            normalized_url=normalize_url(row["url"]),
            canonical_url=row.get("canonical_url"),
            title=row.get("title"),
            h1=row.get("h1"),
            meta_robots=meta_robots,
            indexable=_coerce_bool_from_indexability(row.get("indexability"), meta_robots),
            indexed=None,
            http_status=_coerce_int(row.get("http_status")),
            word_count=_coerce_int(row.get("word_count")),
        )
        db.add(page)

    db.commit()
    return len(parsed_rows)


def get_artifact(db: Session, artifact_id: str) -> Artifact | None:
    return db.scalar(select(Artifact).where(Artifact.id == as_uuid(artifact_id)))
