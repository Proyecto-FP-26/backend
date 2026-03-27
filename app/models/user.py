from __future__ import annotations #Se utiliza para permitir anotaciones de tipo que se refieren a clases que aún no han sido definidas en el código.

from sqlalchemy import func, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List
from datetime import datetime
from enum import Enum
import uuid

from app.db.database import Base

class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    tecnico = "tecnico"

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    passwordHash: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, name="user_role"), default=UserRole.user, nullable=False) 
    isActive: Mapped[bool] = mapped_column(default=True, nullable=False)
    points: Mapped[int] = mapped_column(default=0, nullable=False)
    createdAt: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    reports: Mapped[List[Report]] = relationship("Report", back_populates="user", foreign_keys="[Report.userId]")
    resolved_reports: Mapped[List[Report]] = relationship("Report", back_populates="resolvedBy", foreign_keys="[Report.resolvedById]")
    comments: Mapped[List[Comment]] = relationship(back_populates="user")
    notifications: Mapped[List[Notification]] = relationship(back_populates="user")
    points_entries: Mapped[List[Points]] = relationship(back_populates="user")
    logs: Mapped[List[Log]] = relationship(back_populates="user")
    sessions: Mapped[List[UserSession]] = relationship(back_populates="user")

class UserSession(Base):
    __tablename__ = "users_sessions"
    __table_args__ = {"schema": "auth"}

    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(ForeignKey("auth.users.id"), nullable=False)
    jti: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    deviceInfo: Mapped[str] = mapped_column(nullable=False)
    isRevoked: Mapped[bool] = mapped_column(default=False, nullable=False)
    rememberMe: Mapped[bool] = mapped_column(default=False, nullable=False)
    createdAt: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expiresAt: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="sessions", foreign_keys= [userId])