from datetime import date

from sqlalchemy import JSON, Date, ForeignKey, Integer, Numeric, PrimaryKeyConstraint, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class PageMetricDaily(Base):
    __tablename__ = "page_metrics_daily"
    __table_args__ = (PrimaryKeyConstraint("page_id", "date", name="pk_page_metrics_daily"),)

    page_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("pages.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    impressions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ctr: Mapped[float] = mapped_column(Numeric(8, 5), nullable=False, default=0)
    avg_position: Mapped[float | None] = mapped_column(Numeric(8, 2))
    sessions: Mapped[int | None] = mapped_column(Integer)
    conversions: Mapped[int | None] = mapped_column(Integer)


class RankingDaily(Base):
    __tablename__ = "rankings_daily"
    __table_args__ = (PrimaryKeyConstraint("keyword_id", "date", name="pk_rankings_daily"),)

    keyword_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    ranking_url: Mapped[str | None] = mapped_column(Text)
    rank: Mapped[int | None] = mapped_column(Integer)
    serp_features: Mapped[dict | None] = mapped_column(JSON)
