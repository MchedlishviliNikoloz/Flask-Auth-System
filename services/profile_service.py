from models.user import User
from database import db
from services import username_exists, email_exists
from utils.validators import validate_username, validate_email, validate_password, normalize_bool

from werkzeug.security import generate_password_hash, check_password_hash


def update_general(user_id: int, username: str | None, first_name: str | None, last_name: str | None, bio: str | None) -> dict:
    user = db.session.get(User, user_id)
    if not user:
        return {"success": False, "errors": ["User not found."]}

    if username.lower() == user.username.lower() and first_name == user.profile.first_name and last_name == user.profile.last_name and bio == user.profile.bio:
        return {"success": False, "errors": ["Make some changes before save."]}

    if username and username != user.username:
        username_validation = validate_username(username)
        if not username_validation["success"]:
            return {"success": False, "errors": username_validation["errors"]}

        if username_exists(username):
            return {"success": False, "errors": ["Username already taken."]}

        user.username = username

    if first_name is not None:
        user.profile.first_name = first_name
    if last_name is not None:
        user.profile.last_name = last_name
    if bio is not None:
        user.profile.bio = bio

    db.session.commit()
    return {"success": True, "user": user}

def update_contact(user_id: int, email: str) -> dict:
    user = db.session.get(User, user_id)
    if not user:
        return {"success": False, "errors": ["User not found."]}

    if email and email.lower() == user.email.lower():
        return {"success": False, "errors": ["You are already using this email."]}

    if email and email != user.email:
        email_validation = validate_email(email)
        if not email_validation["success"]:
            return {"success": False, "errors": email_validation["errors"]}

        if email_exists(email):
            return {"success": False, "errors": ["Account with this email already exists."]}

        user.email = email

    db.session.commit()
    return {"success": True, "user": user}

def update_password(user_id: int, current_password: str, new_password: str, confirm_password: str) -> dict:
    user = db.session.get(User, user_id)
    if not user:
        return {"success": False, "errors": ["User not found."]}

    if not current_password or not new_password or not confirm_password:
        return {"success": False, "errors": ["All fields are required."]}

    if confirm_password != new_password:
        return {"success": False, "errors": ["The confirmation password does not match."]}

    if not check_password_hash(user.password, current_password):
        return {"success": False, "errors": ["Current password is incorrect."]}

    if new_password == user.password:
        return {"success": False, "errors": ["You are already using this password."]}

    password_validation = validate_password(new_password, user.username)
    if not password_validation["success"]:
        return {"success": False, "errors": password_validation["errors"]}

    user.password = generate_password_hash(new_password)
    db.session.commit()
    return {"success": True, "user": user}

def update_privacy(user_id: int, is_public: bool) -> dict:
    user = db.session.get(User, user_id)
    if not user:
        return {"success": False, "errors": ["User not found."]}

    try:
        is_public = normalize_bool(is_public)
    except ValueError:
        return {"success": False, "errors": ["Invalid is_public value."]}

    if user.profile.is_public == is_public:
        return {"success": False, "errors": ["Make some changes before save."]}

    user.profile.is_public = is_public
    db.session.commit()
    return {"success": True, "user": user}

def delete_profile(user_id: int, password: str) -> dict:
    user = db.session.get(User, user_id)
    if not user:
        return {"success": False, "errors": ["User not found."]}

    if not password:
        return {"success": False, "errors": ["Password cannot be empty."]}

    if not check_password_hash(user.password, password):
        return {"success": False, "errors": ["Incorrect password."]}

    if user.profile:
        db.session.delete(user.profile)

    db.session.delete(user)
    db.session.commit()
    return {"success": True}