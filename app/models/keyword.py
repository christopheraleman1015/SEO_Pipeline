from sqlalchemy import Numeric, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Keyword(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "keywords"
    __table_args__ = (UniqueConstraint("project_id", "keyword", "locale", name="uq_keywords"),)

    project_id: Mapped[str] = mapped_column(Uuid(as_uuid=True), nullable=False)
    keyword: Mapped[str] = mapped_column(Text, nullable=False)
    locale: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str | None] = mapped_column(Text)
    volume: Mapped[int | None]
    difficulty: Mapped[float | None] = mapped_column(Numeric(8, 2))
    cpc: Mapped[float | None] = mapped_column(Numeric(10, 2))
