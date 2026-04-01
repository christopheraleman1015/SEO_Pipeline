from sqlalchemy import ForeignKey, JSON, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class OpportunityPublication(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "opportunity_publications"

    project_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_draft_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("opportunity_drafts.id", ondelete="CASCADE"), nullable=False
    )
    approved_for_publish: Mapped[bool] = mapped_column(nullable=False, default=False)
    published: Mapped[bool] = mapped_column(nullable=False, default=False)
    target_url: Mapped[str | None] = mapped_column(Text)
    publish_result_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
