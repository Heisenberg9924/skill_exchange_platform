from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class SkillType(str, Enum):
    OFFER = "offer"
    REQUEST = "request"


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    skill_type: Mapped[SkillType] = mapped_column(SqlEnum(SkillType), nullable=False)
    proficiency_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    availability: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    owner = relationship("User", back_populates="skills")
    requested_exchange_requests = relationship(
        "ExchangeRequest",
        back_populates="requested_skill",
        foreign_keys="ExchangeRequest.requested_skill_id",
    )
    offered_exchange_requests = relationship(
        "ExchangeRequest",
        back_populates="offered_skill",
        foreign_keys="ExchangeRequest.offered_skill_id",
    )
