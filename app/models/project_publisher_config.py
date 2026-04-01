from sqlalchemy import ForeignKey, JSON, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ProjectPublisherConfig(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_publisher_configs"

    project_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    mode: Mapped[str] = mapped_column(Text, nullable=False, default="draft")
    config_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
