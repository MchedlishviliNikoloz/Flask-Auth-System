from database import db
from models import User, Follow

def follow_user(follower_id, target_id):
    if follower_id == target_id:
        return {"success": False, "errors": ["You can't follow yourself"]}

    exists = Follow.query.filter_by(
        follower_id=follower_id,
        followed_id=target_id,
    ).first()

    if exists:
        return {"success": False, "errors": ["Already following"]}

    follow = Follow(
        follower_id=follower_id,
        followed_id=target_id
    )

    db.session.add(follow)
    db.session.commit()
    return {"success": True}

def unfollow_user(follower_id, target_id):
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

def get_follow_state(viewer_id: int, target_id: int):
    if not viewer_id:
        return {
            "is_following": False,
            "can_follow": True
        }

    if viewer_id == target_id:
        return {
            "is_following": False,
            "can_follow": False
        }

    follow = Follow.query.filter_by(
        follower_id=viewer_id,
        followed_id=target_id
    ).first()

    is_following = follow is not None

    return {
        "is_following": is_following,
        "can_follow": not is_following
    }