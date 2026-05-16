from flask import Flask, redirect, url_for, render_template, session
from flask_migrate import Migrate

from database import db
from models.user import User
from routes.auth_routes import auth_bp
from routes.profile_routes import profile_bp
from routes.api_routes import api_bp

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret_key'
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