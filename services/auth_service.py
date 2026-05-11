from models.user import User
from models.profile import Profile
from database import db
from utils.validators import validate_username, validate_email, validate_password


def email_exists(email: str) -> bool:
    email_check = db.session.execute(db.select(User).filter_by(email=email)).scalar() is not None
    return email_check

def username_exists(username: str) -> bool:
    username = username.lower()
    username_check = db.session.execute(db.select(User).filter_by(username=username)).scalar() is not None
    return username_check

def get_user_by_username(username: str) -> User:
    return db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()

def get_user_by_email(email: str) -> User:
    return db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()

def get_user_by_id(user_id: int) -> User:
    return db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one_or_none()

def detect_login_input(login_input: str) -> str:
    if "@" in login_input:
        return "email"
    return "username"

def register_user(user: User, profile: Profile):
    user.email = user.email.lower()
    user.username = user.username.lower()

    if username_exists(user.username):
        return {"success": False, "errors": ["Username already exists."],}
    if email_exists(user.email):
        return {"success": False, "errors": ["Email already exists."],}

    username_validation = validate_username(user.username)
    email_validation = validate_email(user.email)
    password_validation = validate_password(user.password, user.username)

    if not username_validation["success"]:
        return {"success": False, "errors": username_validation["errors"],}

    if not email_validation["success"]:
        return {"success": False, "errors": email_validation["errors"],}

    if not password_validation["success"]:
        return {"success": False, "errors": password_validation["errors"],}

    db.session.add(user)
    db.session.commit()
    profile.user_id = user.id
    db.session.add(profile)
    db.session.commit()
    return {"success": True, "user": user}

def authenticate_user(login_input: str, password: str):
    login_input = login_input.lower()
    login_input_type = detect_login_input(login_input)
    if login_input_type == "email":
        user = get_user_by_email(login_input)
        if not user:
            return {"success": False, "errors": ["Email or Password is incorrect."],}

        if not user.check_password(password):
            return {"success": False, "errors": ["Email or Password is incorrect."],}

        return {"success": True, "user": user}

    user = get_user_by_username(login_input)
    if not user:
        return {"success": False, "errors": ["Username or Password is incorrect."], }

    if not user.check_password(password):
        return {"success": False, "errors": ["Username or Password is incorrect."], }

    return {"success": True, "user": user}