from sqlalchemy import ForeignKey, Numeric, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Opportunity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "opportunities"

    project_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    page_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("pages.id", ondelete="SET NULL")
    )
    keyword: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_url: Mapped[str | None] = mapped_column(Text)
    clicks: Mapped[int] = mapped_column(nullable=False, default=0)
    impressions: Mapped[int] = mapped_column(nullable=False, default=0)
    ctr: Mapped[float] = mapped_column(Numeric(8, 5), nullable=False, default=0)
    avg_position: Mapped[float | None] = mapped_column(Numeric(8, 2))
    business_value: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    freshness_need: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    content_gap: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    rankability: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    score: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    reason: Mapped[str | None] = mapped_column(Text)
