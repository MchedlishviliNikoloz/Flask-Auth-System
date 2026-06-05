from database import db
from models.notification import Notification


def create_notification(recipient_id: int, actor_id: int, type: str) -> Notification:
    notification = Notification(
        recipient_id=recipient_id,
        actor_id=actor_id,
        type=type
    )
    db.session.add(notification)
    db.session.commit()
    return notification

def get_notifications(user_id: int) -> list:
    return Notification.query.filter_by(
        recipient_id=user_id
    ).order_by(Notification.created_at.desc()).all()

def get_unread_count(user_id: int) -> int:
    return Notification.query.filter_by(
        recipient_id=user_id,
        is_read=False
    ).count()

def mark_all_read(user_id: int) -> None:
    Notification.query.filter_by(
        recipient_id=user_id,
        is_read=False
    ).update({"is_read": True})
    db.session.commit()

def update_notification_type(recipient_id: int, actor_id: int, old_type: str, new_type: str) -> None:
    notification = Notification.query.filter_by(
        recipient_id=recipient_id,
        actor_id=actor_id,
        type=old_type
    ).first()
    if notification:
        notification.type = new_type
        notification.is_read = False
        db.session.commit()

def delete_notification(notification_id: int, user_id: int) -> dict:
    notification = Notification.query.filter_by(
        id=notification_id,
        recipient_id=user_id
    ).first()
    if not notification:
        return {"success": False, "errors": ["Notification not found."]}
    db.session.delete(notification)
    db.session.commit()
    return {"success": True}

def delete_notification_by_type(recipient_id: int, actor_id: int, type: str) -> None:
    notification = Notification.query.filter_by(
        recipient_id=recipient_id,
        actor_id=actor_id,
        type=type
    ).first()
    if notification:
        db.session.delete(notification)
        db.session.commit()