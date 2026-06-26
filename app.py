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
app.register_blueprint(main_bp)

@app.errorhandler(404)
def not_found(e):
    user = None
    if session.get('user_id'):
        user = db.session.get(User, session['user_id'])
    return render_template('errors/404.html', user=user), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)