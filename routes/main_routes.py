from flask import Blueprint, render_template, redirect, url_for, session
from models import User
from services import get_user_by_username, get_follow_state
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
    logged_user = None
    if session.get('user_id'):
        logged_user = db.session.get(User, session['user_id'])

    searched_user = get_user_by_username(username)
    if not searched_user:
        return render_template('errors/404.html', user=logged_user), 404

    is_own = logged_user and logged_user.id == searched_user.id
    is_follower = logged_user and any(
        f.follower_id == logged_user.id for f in searched_user.followers
    )
    show_full = searched_user.profile.is_public or is_own or is_follower

    follow_state = get_follow_state(
        logged_user.id if logged_user else None,
        searched_user.id
    )

    return render_template('main/user.html',
        searched_user=searched_user,
        user=logged_user,
        show_full=show_full,
        is_own=is_own,
        follow_state=follow_state
    )