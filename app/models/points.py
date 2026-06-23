from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ReasonPoints(Base):
    __tablename__ = "reason_points"
    __table_args__ = {"schema": "points"}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    points_entries: Mapped[List["Points"]] = relationship(back_populates="reason")


class Points(Base):
    __tablename__ = "points"
    __table_args__ = {"schema": "points"}

    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(ForeignKey("auth.users.id"), nullable=False)
    points: Mapped[int] = mapped_column(nullable=False)
    reasonId: Mapped[int] = mapped_column(
        ForeignKey("points.reason_points.id"), nullable=False
    )
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="points_entries")
    reason: Mapped[ReasonPoints] = relationship(back_populates="points_entries")
