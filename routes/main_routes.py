from flask import Blueprint, render_template, redirect, url_for, session
from models import User
from services import get_user_by_username
from database import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
def home():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    user = db.session.get(User, user_id)
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
    return render_template('main/index.html', user=user)

@main_bp.route('/u/<username>')
def user_profile(username):
    user = get_user_by_username(username)
    if not user:
        return render_template('errors/404.html'), 404
    return render_template('main/user.html', user=user)