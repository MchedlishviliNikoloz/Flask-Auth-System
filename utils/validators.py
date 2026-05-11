USERNAME_ERROR_MSGS = {
    "username_length": "Username length must be between 3 and 20 characters long.",
    "username_empty": "Username cannot be empty.",
    "contains_space": "Username cannot contain spaces.",
    "username_lowercase": "Username must contain only lowercase letters.",
    "special_characters": "Only letters, numbers and these special characters are allowed: '_', '.', '-'",
}
EMAIL_ERROR_MSGS = {
    "invalid_format": "Email format is invalid.",
    "email_empty": "Email cannot be empty."
}
PASSWORD_ERROR_MSGS = {
    "too_short": "Password must be at least 8 characters long.",
    "too_long": "Password cannot exceed 64 characters.",
    "password_empty": "Password cannot be empty.",
    "contains_username": "Password cannot contain your username.",
    "contains_space": "Password cannot contain spaces.",
    "no_uppercase": "Password must contain at least one uppercase letter.",
    "no_number": "Password must contain at least one number."
}
disallowed_special_chars = [
    '!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
    '+', '=', '[', ']', '{', '}', ';', ':', "'", '"', '\\',
    '|', '<', '>', ',', '?', '/', '`', '~'
]
allowed_special_chars = ['_', '.', '-']

def validate_username(username: str) -> dict:
    if not username:
        return {"success": False, "errors": [USERNAME_ERROR_MSGS["username_empty"]]}

    errors = []

    if not (3 <= len(username) <= 20):
        errors.append(USERNAME_ERROR_MSGS["username_length"])

    if " " in username:
        errors.append(USERNAME_ERROR_MSGS["contains_space"])

    if any(char.isupper() for char in username):
        errors.append(USERNAME_ERROR_MSGS["username_lowercase"])

    allowed_set = set(allowed_special_chars)
    for char in username:
        if not (char.isalnum() or char in allowed_set):
            errors.append(USERNAME_ERROR_MSGS["special_characters"])
            break

    return {"success": not errors, "errors": errors}


def validate_email(email: str) -> dict:
    if not email:
        return {"success": False, "errors": [EMAIL_ERROR_MSGS["email_empty"]]}

    errors = []

    if "@" not in email:
        return {"success": False, "errors": [EMAIL_ERROR_MSGS["invalid_format"]]}

    if email.count("@") != 1:
        return {"success": False, "errors": [EMAIL_ERROR_MSGS["invalid_format"]]}

    first_part, domain_part = email.split("@")

    if not first_part:
        return {"success": False, "errors": [EMAIL_ERROR_MSGS["invalid_format"]]}

    if not domain_part:
        return {"success": False, "errors": [EMAIL_ERROR_MSGS["invalid_format"]]}

    if "." not in domain_part:
        return {"success": False, "errors": [EMAIL_ERROR_MSGS["invalid_format"]]}

    if domain_part[0] == "." or domain_part[-1] == ".":
        return {"success": False, "errors": [EMAIL_ERROR_MSGS["invalid_format"]]}

    return {"success": True, "errors": errors}

def validate_password(password: str, username: str) -> dict:
    if not password:
        return {"success": False, "errors": [PASSWORD_ERROR_MSGS["password_empty"]]}

    errors = []

    if len(password) < 8:
        errors.append(PASSWORD_ERROR_MSGS["too_short"])
    elif len(password) > 64:
        errors.append(PASSWORD_ERROR_MSGS["too_long"])

    if " " in password:
        errors.append(PASSWORD_ERROR_MSGS["contains_space"])

    if username and len(username) >= 3 and username.lower() in password.lower():
        errors.append(PASSWORD_ERROR_MSGS["contains_username"])

    if not any(char.isupper() for char in password):
        errors.append(PASSWORD_ERROR_MSGS["no_uppercase"])
    if not any(char.isdigit() for char in password):
        errors.append(PASSWORD_ERROR_MSGS["no_number"])

    return {"success": not errors, "errors": errors}
