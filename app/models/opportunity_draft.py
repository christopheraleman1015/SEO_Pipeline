from sqlalchemy import ForeignKey, Integer, JSON, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class OpportunityDraft(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "opportunity_drafts"
    __table_args__ = (
        UniqueConstraint("opportunity_brief_id", "version", name="uq_opportunity_drafts_brief_version"),
    )

    project_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_brief_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("opportunity_briefs.id", ondelete="CASCADE"), nullable=False
    )
    target_page_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("pages.id", ondelete="SET NULL")
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="draft")
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    qa_json: Mapped[dict] = mapped_column(JSON, nullable=False)
