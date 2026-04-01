from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Numeric, PrimaryKeyConstraint, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class QueryMetricDaily(Base):
    __tablename__ = "query_metrics_daily"
    __table_args__ = (PrimaryKeyConstraint("project_id", "query", "date", name="pk_query_metrics_daily"),)

    project_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    page_url: Mapped[str | None] = mapped_column(Text)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    impressions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ctr: Mapped[float] = mapped_column(Numeric(8, 5), nullable=False, default=0)
    avg_position: Mapped[float | None] = mapped_column(Numeric(8, 2))
