from flask import Flask, render_template, request, redirect, url_for, session
from flask_migrate import Migrate

from database import db
from models.user import User
from models.profile import Profile
from services.auth_service import register_user, authenticate_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret_key'
DB_PATH = "database.db"

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
db.init_app(app)

migrate = Migrate(app, db)

@app.route('/')
@app.route('/home')
def home():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get("user_id")
    user = db.session.get(User, user_id)
    return render_template('main/index.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

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
            return render_template('auth/register.html', errors=result['errors'])

        session['user_id'] = result['user'].id

        return redirect(url_for('home'))

    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        login_input = request.form['login_input']
        password = request.form['password']

        result = authenticate_user(login_input, password)
        if not result['success']:
            return render_template('auth/login.html', errors=result['errors'])

        session['user_id'] = result['user'].id

        return redirect(url_for('home'))

    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)