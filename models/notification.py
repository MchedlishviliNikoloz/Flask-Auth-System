from database import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone


class Notification(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        nullable=False
    )
    actor_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        nullable=False
    )
    type: Mapped[str] = mapped_column(nullable=False)
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)
    recipient: Mapped["User"] = relationship(
        "User",
        foreign_keys=[recipient_id],
        back_populates="notifications"
    )
    actor: Mapped["User"] = relationship(
        "User",
        foreign_keys=[actor_id]
    )
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )