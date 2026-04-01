from sqlalchemy import ForeignKey, Numeric, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class InternalLinkOpportunity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "internal_link_opportunities"

    project_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    source_page_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("pages.id", ondelete="SET NULL")
    )
    target_page_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("pages.id", ondelete="SET NULL")
    )
    cluster_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("opportunity_clusters.id", ondelete="SET NULL")
    )
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    target_url: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_anchor: Mapped[str] = mapped_column(Text, nullable=False)
    overlap_score: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    target_score: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    score: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    reason: Mapped[str | None] = mapped_column(Text)
