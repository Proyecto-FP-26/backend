from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class NotificationType(Base):
    __tablename__ = "notifications_type"
    __table_args__ = {"schema": "notifications"}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    notifications: Mapped[List["Notification"]] = relationship(back_populates="type")


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = {"schema": "notifications"}

    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(ForeignKey("auth.users.id"), nullable=False)
    reportId: Mapped[int | None] = mapped_column(
        ForeignKey("reports.reports.id"), nullable=True
    )
    message: Mapped[str] = mapped_column(nullable=False)
    isRead: Mapped[bool] = mapped_column(default=False, nullable=False)
    typeId: Mapped[int | None] = mapped_column(
        ForeignKey("notifications.notifications_type.id"), nullable=True
    )
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="notifications")
    report: Mapped[Report | None] = relationship(back_populates="notifications")
    type: Mapped[NotificationType | None] = relationship(back_populates="notifications")
