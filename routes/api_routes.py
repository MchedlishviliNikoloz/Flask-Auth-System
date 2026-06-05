from flask import Blueprint, request, session
from models.user import User
from database import db
from models.profile import Profile
from services import (register_user, authenticate_user, username_exists, email_exists,
                      get_notifications, mark_all_read, get_unread_count, delete_notification)
from services import (update_general, update_contact, update_password, delete_profile,
                      update_privacy, get_user_by_username, accept_request, reject_request, get_pending_requests)

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/register', methods=['POST'])
def api_register():
    if session.get('user_id'):
        return {"success": False, "errors": ["Already logged in."]}, 400

    data = request.json

    username = data.get('username')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')

    user = User(
        username=username,
        email=email,
        password=password
    )
    profile = Profile(
        first_name=first_name,
        last_name=last_name,
    )

    result = register_user(user, profile)
    if not result['success']:
        return {"success": False, "errors": result['errors']}, 400

    session['user_id'] = result['user'].id
    return {"success": True, "message": "User Created Successfully.","data": result["user"].to_dict()}, 201

@api_bp.route('/api/login', methods=['POST'])
def api_login():
    if session.get('user_id'):
        return {"success": False, "errors": ["Already logged in."]}, 400

    data = request.json

    login_input = data.get('login_input')
    password = data.get('password')

    result = authenticate_user(login_input, password)
    if not result['success']:
        return {"success": False, "errors": result['errors']}, 400

    session['user_id'] = result['user'].id
    return {"success": True, "message": "User Logged In Successfully.", "data": result["user"].to_dict()}, 200

@api_bp.route('/api/logout', methods=['POST'])
def api_logout():
    if not session.get('user_id'):
        return {"success": False, "errors": ["No active session found."]}, 400
    session.pop('user_id', None)
    return {"success": True, "message": "User Logged out Successfully."}, 200

@api_bp.route('/api/user/me', methods=['GET'])
def api_me():
    if not session.get('user_id'):
        return {"success": False, "errors": ["No active session found."]}, 400
    user = db.session.get(User, session['user_id'])
    if not user:
        return {"success": False, "errors": ["User not found."]}, 404
    user_dict = user.to_dict()
    user_dict['first_name'] = user.profile.first_name
    user_dict['last_name'] = user.profile.last_name
    user_dict['bio'] = user.profile.bio

    return {"success": True, "data": user_dict}, 200

@api_bp.route('/api/profile/general', methods=['PATCH'])
def api_profile_general():
    if not session.get('user_id'):
        return {"success": False, "errors": ["No active session found."]}, 400
    data = request.json

    user_id = session.get('user_id')
    username = data.get('username')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    bio = data.get('bio')

    result = update_general(user_id, username, first_name, last_name, bio)

    if not result['success']:
        return {"success": False, "errors": result["errors"]}, 400

    user = db.session.get(User, user_id)
    result_data = {
        'username': user.username,
        'first_name': user.profile.first_name,
        'last_name': user.profile.last_name,
        'bio': user.profile.bio,
    }

    return {"success": True, "data": result_data, "message": "Changes saved successfully."}, 200

@api_bp.route('/api/profile/contact', methods=['PATCH'])
def api_profile_contact():
    if not session.get('user_id'):
        return {"success": False, "errors": ["No active session found."]}, 400
    data = request.json

    user_id = session.get('user_id')
    email = data.get('email')

    result = update_contact(user_id, email)

    user = db.session.get(User, user_id)
    if not result['success']:
        return {"success": False, "errors": result['errors']}, 400

    return {"success": True, "data": user.to_dict(), "message": "Email updated successfully."}, 200

@api_bp.route('/api/profile/password', methods=['PATCH'])
def api_profile_password():
    if not session.get('user_id'):
        return {"success": False, "errors": ["No active session found."]}, 400
    data = request.json

    user_id = session.get('user_id')
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    result = update_password(user_id, current_password, new_password, confirm_password)
    if not result['success']:
        return {"success": False, "errors": result['errors']}, 400

    return {"success": True, "message": "Password updated successfully."}, 200

@api_bp.route('/api/profile/privacy', methods=['POST'])
def profile_privacy():
    if not session.get('user_id'):
        return {"success": False, "errors": ["No active session found."]}, 400
    data = request.json

    user_id = session.get('user_id')
    is_public = data.get('is_public')
    result = update_privacy(user_id, is_public)

    if not result['success']:
        return {"success": False, "errors": result['errors']}, 400

    return {"success": True, "message": "Profile privacy updated successfully."}, 200

@api_bp.route('/api/profile/delete', methods=['DELETE'])
def api_profile_delete():
    if not session.get('user_id'):
        return {"success": False, "errors": ["No active session found."]}, 400
    data = request.json

    user_id = session.get('user_id')
    password = data.get('password')
    result = delete_profile(user_id, password)

    if not result['success']:
        return {"success": False, "errors": result['errors']}, 400

    session.clear()
    return {"success": True, "message": "Profile deleted successfully."}, 200

@api_bp.route('/api/check/username', methods=['GET'])
def api_check_username():
    username = request.args.get('username', '').lower()
    if not username:
        return {"available": False}, 400
    exists = username_exists(username)
    return {"available": not exists}, 200

@api_bp.route('/api/check/email', methods=['GET'])
def api_check_email():
    email = request.args.get('email', '').lower()
    if not email:
        return {"available": False}, 400
    exists = email_exists(email)
    return {"available": not exists}, 200

@api_bp.route('/api/u/<username>/followers', methods=['GET'])
def api_followers(username):
    user = get_user_by_username(username)
    if not user:
        return {"users": []}, 404
    offset = int(request.args.get('offset', 0))
    limit  = int(request.args.get('limit', 15))
    follows = user.followers[offset:offset + limit]
    users = [{
        "username": f.follower.username,
        "display_name": (f.follower.profile.first_name or '') + ' ' + (f.follower.profile.last_name or '')
    } for f in follows]
    return {"users": users}, 200

@api_bp.route('/api/u/<username>/following', methods=['GET'])
def api_following(username):
    user = get_user_by_username(username)
    if not user:
        return {"users": []}, 404
    offset = int(request.args.get('offset', 0))
    limit  = int(request.args.get('limit', 15))
    follows = user.following[offset:offset + limit]
    users = [{
        "username": f.followed.username,
        "display_name": (f.followed.profile.first_name or '') + ' ' + (f.followed.profile.last_name or '')
    } for f in follows]
    return {"users": users}, 200

@api_bp.route('/api/u/<username>/accept-request', methods=['POST'])
def api_accept_request(username):
    if not session.get('user_id'):
        return {"success": False, "errors": ["No active session found."]}, 400

    requester = get_user_by_username(username)
    if not requester:
        return {"success": False, "errors": ["User not found"]}, 404

    target_id = session.get('user_id')

    result = accept_request(target_id, requester.id)

    if not result["success"]:
        return result, 400

    return {"success": True, "message": "Request accepted."}, 200

@api_bp.route('/api/u/<username>/reject-request', methods=['POST'])
def api_reject_request(username):
    if not session.get('user_id'):
        return {"success": False, "errors": ["No active session found."]}, 400

    requester = get_user_by_username(username)
    if not requester:
        return {"success": False, "errors": ["User not found"]}, 404

    target_id = session.get('user_id')

    result = reject_request(target_id, requester.id)

    if not result["success"]:
        return result, 400

    return {"success": True, "message": "Request rejected."}, 200

@api_bp.route('/api/me/pending-requests', methods=['GET'])
def api_pending_requests():
    if not session.get('user_id'):
        return {"success": False, "errors": ["No active session found."]}, 401

    user_id = session.get('user_id')

    requests = get_pending_requests(user_id)

    users = [{
        "username": r.requester.username,
        "display_name": (r.requester.profile.first_name or '') + ' ' + (r.requester.profile.last_name or ''),
        "created_at": r.created_at.isoformat()
    } for r in requests]

    return {"success": True, "users": users}, 200

@api_bp.route('/api/notifications', methods=['GET'])
def api_notifications():
    if not session.get('user_id'):
        return {"success": False, "errors": ["No active session found."]}, 401

    user_id = session.get('user_id')
    notifications = get_notifications(user_id)

    result = [{
        "id": n.id,
        "type": n.type,
        "actor_username": n.actor.username,
        "actor_display_name": (n.actor.profile.first_name or '') + ' ' + (n.actor.profile.last_name or ''),
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat()
    } for n in notifications]

    mark_all_read(user_id)
    return {"success": True, "notifications": result}, 200

@api_bp.route('/api/notifications/unread-count', methods=['GET'])
def api_unread_count():
    if not session.get('user_id'):
        return {"success": False, "errors": ["No active session found."]}, 401
    count = get_unread_count(session.get('user_id'))
    return {"count": count}, 200

@api_bp.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
def api_delete_notification(notification_id):
    if not session.get('user_id'):
        return {"success": False, "errors": ["No active session found."]}, 401
    result = delete_notification(notification_id, session.get('user_id'))
    if not result["success"]:
        return result, 400
    return {"success": True}, 200