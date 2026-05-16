from flask import Blueprint, request, session
from models.user import User
from database import db
from models.profile import Profile
from services.auth_service import register_user, authenticate_user
from services.profile_service import update_general, update_contact, update_password, delete_profile

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