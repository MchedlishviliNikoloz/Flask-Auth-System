from flask import Blueprint, render_template, request, redirect, url_for, session
from models.user import User
from database import db
from services.profile_service import update_general, update_contact, update_password, delete_profile

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET'])
def profile():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    user = db.session.get(User, user_id)
    return render_template('profile/profile.html', user=user)


@profile_bp.route('/profile/general', methods=['POST'])
def profile_general():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    username = request.form.get('username')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    bio = request.form.get('bio')

    result = update_general(user_id, username, first_name, last_name, bio)

    user = db.session.get(User, user_id)
    if not result['success']:
        return render_template('profile/profile.html', user=user, errors=result['errors'], active_section='general')

    return render_template('profile/profile.html', user=user, success=True, active_section='general')

@profile_bp.route('/profile/contact', methods=['POST'])
def profile_contact():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    email = request.form.get('email')

    result = update_contact(user_id, email)

    user = db.session.get(User, user_id)
    if not result['success']:
        return render_template('profile/profile.html', user=user, errors=result['errors'], active_section='contact')

    return render_template('profile/profile.html', user=user, success=True, active_section='contact')

@profile_bp.route('/profile/password', methods=['POST'])
def profile_password():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    result = update_password(user_id, current_password, new_password, confirm_password)

    user = db.session.get(User, user_id)
    if not result['success']:
        return render_template('profile/profile.html', user=user, errors=result['errors'], active_section='password')

    return render_template('profile/profile.html', user=user, success=True, active_section='password')

@profile_bp.route('/profile/delete', methods=['POST'])
def profile_delete():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    password = request.form.get('password')

    result = delete_profile(user_id, password)

    if not result['success']:
        user = db.session.get(User, user_id)
        return render_template('profile/profile.html', user=user, errors=result['errors'], active_section='danger')

    session.clear()
    return redirect(url_for('auth.register'))