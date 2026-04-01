from sqlalchemy import Boolean, ForeignKey, Numeric, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Cluster(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "clusters"

    project_id: Mapped[str] = mapped_column(Uuid(as_uuid=True), nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    primary_intent: Mapped[str | None] = mapped_column(Text)
    target_page_type: Mapped[str | None] = mapped_column(Text)
    target_page_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    score: Mapped[float | None] = mapped_column(Numeric(8, 4))
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")


class ClusterKeyword(Base):
    __tablename__ = "cluster_keywords"

    cluster_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("clusters.id", ondelete="CASCADE"), primary_key=True
    )
    keyword_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    serp_overlap: Mapped[float | None] = mapped_column(Numeric(8, 4))
