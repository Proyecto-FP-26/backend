from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Log(Base):
    __tablename__ = "logs"
    __table_args__ = {"schema": "logs"}

    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int | None] = mapped_column(
        ForeignKey("auth.users.id"), nullable=True
    )
    action: Mapped[str]
    entity: Mapped[str]
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User | None] = relationship(back_populates="logs")
