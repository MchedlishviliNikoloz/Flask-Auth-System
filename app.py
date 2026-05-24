from flask import Flask, redirect, url_for, render_template, session
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

from database import db
from models import User
from routes import *

app = Flask(__name__)

load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DB_PATH = "database.db"

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
db.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(api_bp)

@app.route('/')
@app.route('/home')
def home():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    user_id = session.get("user_id")
    user = db.session.get(User, user_id)
    return render_template('main/index.html', user=user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)