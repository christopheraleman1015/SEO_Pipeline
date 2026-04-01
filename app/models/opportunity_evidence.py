from sqlalchemy import ForeignKey, JSON, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class OpportunityEvidence(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "opportunity_evidence"

    project_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_brief_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("opportunity_briefs.id", ondelete="CASCADE"), nullable=False
    )
    artifact_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("artifacts.id", ondelete="SET NULL")
    )
    evidence_type: Mapped[str] = mapped_column(Text, nullable=False, default="note")
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content_text: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
