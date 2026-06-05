from database import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from werkzeug.security import check_password_hash

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    profile: Mapped["Profile"] = relationship(
        back_populates="user", uselist=False
    )
    followers: Mapped[list["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.followed_id",
        back_populates="followed",
        cascade="all, delete-orphan"
    )
    following: Mapped[list["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan"
    )
    sent_requests: Mapped[list["FollowRequest"]] = relationship(
        "FollowRequest",
        foreign_keys="FollowRequest.requester_id",
        back_populates="requester",
        cascade="all, delete-orphan"
    )
    received_requests: Mapped[list["FollowRequest"]] = relationship(
        "FollowRequest",
        foreign_keys="FollowRequest.target_id",
        back_populates="target",
        cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        foreign_keys="Notification.recipient_id",
        back_populates="recipient",
        cascade="all, delete-orphan",
        order_by="Notification.created_at.desc()"
    )
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)