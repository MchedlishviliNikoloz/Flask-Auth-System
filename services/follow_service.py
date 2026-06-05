from database import db
from models import User, Follow
from models.follow_request import FollowRequest
from services.notification_service import create_notification, update_notification_type
from services.auth_service import get_user_by_id


def follow_user(follower_id: int, target_id: int) -> dict:
    if follower_id == target_id:
        return {"success": False, "errors": ["You can't follow yourself"]}

    exists = Follow.query.filter_by(
        follower_id=follower_id,
        followed_id=target_id,
    ).first()

    if exists:
        return {"success": False, "errors": ["Already following"]}

    target_user = get_user_by_id(target_id)

    if not target_user:
        return {"success": False, "errors": ["User not found"]}

    if not target_user.profile.is_public:
        request_exists = FollowRequest.query.filter_by(
            requester_id=follower_id,
            target_id=target_id,
        ).first()
        if request_exists:
            return {"success": False, "errors": ["Already requested"]}

        follow_request = FollowRequest(
            requester_id=follower_id,
            target_id=target_id,
        )
        db.session.add(follow_request)
        db.session.commit()
        create_notification(
            recipient_id=target_id,
            actor_id=follower_id,
            type='follow_request'
        )
        return {"success": True, "status": "requested"}


    follow = Follow(
        follower_id=follower_id,
        followed_id=target_id
    )

    db.session.add(follow)
    db.session.commit()
    create_notification(
        recipient_id=target_id,
        actor_id=follower_id,
        type='new_follower'
    )
    return {"success": True, "status": "followed"}

def unfollow_user(follower_id: int, target_id: int) -> dict:
    if follower_id == target_id:
        return {"success": False, "errors": ["You can't unfollow yourself"]}

    follow = Follow.query.filter_by(
        follower_id=follower_id,
        followed_id=target_id,
    ).first()

    if follow:
        db.session.delete(follow)
        db.session.commit()
    else:
        return {"success": False, "errors": ["You are not following this user"]}

    return {"success": True}
def get_follow_state(viewer_id: int, target_id: int) -> dict:
    if not viewer_id:
        return {
            "is_following": False,
            "has_requested": False,
            "can_follow": True
        }

    if viewer_id == target_id:
        return {
            "is_following": False,
            "has_requested": False,
            "can_follow": False
        }

    follow = Follow.query.filter_by(
        follower_id=viewer_id,
        followed_id=target_id
    ).first()

    if follow:
        return {
            "is_following": True,
            "has_requested": False,
            "can_follow": False
        }

    request = FollowRequest.query.filter_by(
        requester_id=viewer_id,
        target_id=target_id
    ).first()

    if request:
        return {
            "is_following": False,
            "has_requested": True,
            "can_follow": False
        }

    return {
        "is_following": False,
        "has_requested": False,
        "can_follow": True
    }

def accept_request(target_id: int, requester_id: int) -> dict:
    follow_request = FollowRequest.query.filter_by(
        requester_id=requester_id,
        target_id=target_id,
    ).first()

    if not follow_request:
        return {"success": False, "errors": ["Request not found"]}

    follow_exists = Follow.query.filter_by(
        follower_id=requester_id,
        followed_id=target_id,
    ).first()

    if follow_exists:
        return {"success": False, "errors": ["Already following"]}

    follow = Follow(
        follower_id=requester_id,
        followed_id=target_id,
    )

    db.session.add(follow)
    db.session.delete(follow_request)
    db.session.commit()
    update_notification_type(
        recipient_id=target_id,
        actor_id=requester_id,
        old_type='follow_request',
        new_type='now_following'
    )
    create_notification(
        recipient_id=requester_id,
        actor_id=target_id,
        type='follow_accepted'
    )
    return {"success": True}

def reject_request(target_id: int, requester_id: int) -> dict:
    follow_request = FollowRequest.query.filter_by(
        requester_id=requester_id,
        target_id=target_id,
    ).first()

    if not follow_request:
        return {"success": False, "errors": ["Request not found"]}

    db.session.delete(follow_request)
    db.session.commit()
    return {"success": True}

def cancel_request(requester_id: int, target_id: int) -> dict:
    follow_request = FollowRequest.query.filter_by(
        requester_id=requester_id,
        target_id=target_id,
    ).first()

    if not follow_request:
        return {"success": False, "errors": ["Request not found"]}

    db.session.delete(follow_request)
    db.session.commit()
    return {"success": True}

def get_pending_requests(user_id: int):
    user = get_user_by_id(user_id)
    if not user:
        return {"success": False, "errors": ["User not found"]}

    follow_requests = user.received_requests

    return follow_requests