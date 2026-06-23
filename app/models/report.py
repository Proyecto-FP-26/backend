from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ReportStatus(str, Enum):
    PENDIENTE = "pendiente"
    EN_REVISION = "en revisión"
    RESUELTO = "resuelto"


class ReportPriority(str, Enum):
    LOW = "low"
    MID = "mid"
    HIGH = "high"


class ReportCategory(Base):
    __tablename__ = "report_category"
    __table_args__ = {"schema": "reports"}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(nullable=True)
    icon: Mapped[str | None] = mapped_column(nullable=True)

    reports: Mapped[List["Report"]] = relationship(back_populates="category")


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = {"schema": "reports"}

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        SQLEnum(ReportStatus, name="report_status"),
        default=ReportStatus.PENDIENTE,
        nullable=False,
    )
    userId: Mapped[int] = mapped_column(ForeignKey("auth.users.id"), nullable=False)
    resolvedById: Mapped[int | None] = mapped_column(
        ForeignKey("auth.users.id"), nullable=True
    )
    priority: Mapped[ReportPriority] = mapped_column(
        SQLEnum(ReportPriority, name="report_priority"),
        default=ReportPriority.MID,
        nullable=False,
    )
    categoryId: Mapped[int] = mapped_column(
        ForeignKey("reports.report_category.id"), nullable=False
    )
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped[User] = relationship(
        "User", back_populates="reports", foreign_keys=[userId]
    )
    resolvedBy: Mapped[User | None] = relationship(
        "User", back_populates="resolved_reports", foreign_keys=[resolvedById]
    )
    category: Mapped[ReportCategory] = relationship(back_populates="reports")
    images: Mapped[List[ReportImage]] = relationship(back_populates="report")
    comments: Mapped[List[Comment]] = relationship(back_populates="report")
    notifications: Mapped[List[Notification]] = relationship(back_populates="report")


class ReportImage(Base):
    __tablename__ = "report_images"
    __table_args__ = {"schema": "reports"}

    id: Mapped[int] = mapped_column(primary_key=True)
    reportId: Mapped[int] = mapped_column(
        ForeignKey("reports.reports.id"), nullable=False
    )
    imageUrl: Mapped[str] = mapped_column(nullable=False)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    report: Mapped["Report"] = relationship(back_populates="images")


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = {"schema": "reports"}

    id: Mapped[int] = mapped_column(primary_key=True)
    reportId: Mapped[int] = mapped_column(
        ForeignKey("reports.reports.id"), nullable=False
    )
    userId: Mapped[int] = mapped_column(ForeignKey("auth.users.id"), nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    report: Mapped[Report] = relationship(back_populates="comments")
    user: Mapped[User] = relationship(back_populates="comments")
