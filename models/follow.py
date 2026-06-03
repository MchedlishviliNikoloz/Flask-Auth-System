from database import db
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone


class Follow(db.Model):
    __table_args__ = (
        UniqueConstraint(
            "follower_id",
            "followed_id",
            name="uq_follow_relationship"
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        nullable=False
    )
    followed_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        nullable=False
    )
    follower: Mapped["User"] = relationship(
        "User",
        foreign_keys=[follower_id],
        back_populates="following"
    )
    followed: Mapped["User"] = relationship(
        "User",
        foreign_keys=[followed_id],
        back_populates="followers"
    )
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )