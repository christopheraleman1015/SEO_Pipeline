from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    locale: Mapped[str] = mapped_column(Text, nullable=False, default="en-US")
    timezone: Mapped[str] = mapped_column(Text, nullable=False, default="America/Chicago")
    cms_type: Mapped[str | None] = mapped_column(Text)

    pages = relationship("Page", back_populates="project", cascade="all, delete-orphan")
