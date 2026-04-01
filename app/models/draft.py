from sqlalchemy import JSON, ForeignKey, Integer, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Draft(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "drafts"
    __table_args__ = (UniqueConstraint("brief_id", "version", name="uq_drafts_brief_version"),)

    brief_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("briefs.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="draft")
    content_markdown: Mapped[str | None] = mapped_column(Text)
    evidence_report: Mapped[dict | None] = mapped_column(JSON)
    qa_report: Mapped[dict | None] = mapped_column(JSON)
