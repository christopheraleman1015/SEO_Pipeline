from sqlalchemy import JSON, ForeignKey, Integer, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Brief(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "briefs"
    __table_args__ = (UniqueConstraint("cluster_id", "version", name="uq_briefs_cluster_version"),)

    project_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    cluster_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("clusters.id", ondelete="CASCADE"), nullable=False
    )
    target_page_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("pages.id", ondelete="SET NULL")
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="draft")
    brief_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    prompt_version: Mapped[str | None] = mapped_column(Text)
