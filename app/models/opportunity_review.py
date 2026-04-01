from sqlalchemy import ForeignKey, Integer, JSON, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class OpportunityReview(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "opportunity_reviews"
    __table_args__ = (
        UniqueConstraint("opportunity_draft_id", "version", name="uq_opportunity_reviews_draft_version"),
    )

    project_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_draft_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("opportunity_drafts.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="reviewed")
    review_json: Mapped[dict] = mapped_column(JSON, nullable=False)
