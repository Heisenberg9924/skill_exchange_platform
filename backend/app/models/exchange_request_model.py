from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ExchangeRequestStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ExchangeRequest(Base):
    __tablename__ = "exchange_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    requested_skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE")
    )
    offered_skill_id: Mapped[int | None] = mapped_column(
        ForeignKey("skills.id", ondelete="SET NULL"),
        nullable=True,
    )
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ExchangeRequestStatus] = mapped_column(
        SqlEnum(ExchangeRequestStatus),
        default=ExchangeRequestStatus.PENDING,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    requester = relationship(
        "User",
        back_populates="sent_exchange_requests",
        foreign_keys=[requester_id],
    )
    recipient = relationship(
        "User",
        back_populates="received_exchange_requests",
        foreign_keys=[recipient_id],
    )
    requested_skill = relationship(
        "Skill",
        back_populates="requested_exchange_requests",
        foreign_keys=[requested_skill_id],
    )
    offered_skill = relationship(
        "Skill",
        back_populates="offered_exchange_requests",
        foreign_keys=[offered_skill_id],
    )
    chat_thread = relationship(
        "ChatThread",
        back_populates="exchange_request",
        uselist=False,
        cascade="all, delete-orphan",
    )
