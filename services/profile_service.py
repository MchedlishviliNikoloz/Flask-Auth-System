from models.user import User
from models.profile import Profile
from database import db
from services.auth_service import username_exists, email_exists
from utils.validators import validate_username, validate_email, validate_password


def update_general(user_id: int, username: str | None, first_name: str | None, last_name: str | None, bio: str | None) -> dict:
    user = db.session.get(User, user_id)
    if not user:
        return {"success": False, "errors": ["User not found."]}

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

    if email and email != user.email:
        email_validation = validate_email(email)
        if not email_validation["success"]:
            return {"success": False, "errors": email_validation["errors"]}

        if email_exists(email):
            return {"success": False, "errors": ["Account with this email already exists."]}

        user.email = email

    db.session.commit()
    return {"success": True, "user": user}


def update_password(user_id: int, current_password: str, new_password: str) -> dict:
    user = db.session.get(User, user_id)
    if not user:
        return {"success": False, "errors": ["User not found."]}

    if user.password != current_password:
        return {"success": False, "errors": ["Current password is incorrect."]}

    if new_password == user.password:
        return {"success": False, "errors": ["You are already using this password."]}

    password_validation = validate_password(new_password, user.username)
    if not password_validation["success"]:
        return {"success": False, "errors": password_validation["errors"]}

    user.password = new_password
    db.session.commit()
    return {"success": True, "user": user}

def delete_profile(user_id: int, password: str) -> dict:
    user = db.session.get(User, user_id)
    if not user:
        return {"success": False, "errors": ["User not found."]}

    if not password:
        return {"success": False, "errors": ["Password cannot be empty."]}

    if user.password != password:
        return {"success": False, "errors": ["Incorrect password."]}

    if user.profile:
        db.session.delete(user.profile)

    db.session.delete(user)
    db.session.commit()
    return {"success": True}