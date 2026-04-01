from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project_publisher_config import ProjectPublisherConfig
from app.utils.ids import as_uuid


def upsert_project_publisher_config(
    db: Session, project_id: str, provider: str, mode: str, config_json: dict
) -> ProjectPublisherConfig:
    project_uuid = as_uuid(project_id)
    config = db.scalar(
        select(ProjectPublisherConfig).where(ProjectPublisherConfig.project_id == project_uuid)
    )
    if config is None:
        config = ProjectPublisherConfig(
            project_id=project_uuid,
            provider=provider,
            mode=mode,
            config_json=config_json,
        )
        db.add(config)
    else:
        config.provider = provider
        config.mode = mode
        config.config_json = config_json
        db.add(config)

    db.commit()
    db.refresh(config)
    return config


def get_project_publisher_config(db: Session, project_id: str) -> ProjectPublisherConfig | None:
    return db.scalar(
        select(ProjectPublisherConfig).where(ProjectPublisherConfig.project_id == as_uuid(project_id))
    )
