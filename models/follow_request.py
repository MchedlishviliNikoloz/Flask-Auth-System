from database import db
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone


class FollowRequest(db.Model):
    __table_args__ = (
        UniqueConstraint(
            "requester_id",
            "target_id",
            name="uq_follow_request"
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    requester_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        nullable=False
    )
    target_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        nullable=False
    )
    requester: Mapped["User"] = relationship(
        "User",
        foreign_keys=[requester_id],
        back_populates="sent_requests"
    )
    target: Mapped["User"] = relationship(
        "User",
        foreign_keys=[target_id],
        back_populates="received_requests"
    )
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )