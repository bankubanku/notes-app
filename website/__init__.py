from flask import Flask
from flask_login import LoginManager
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

db = SQLAlchemy()
DB_NAME = 'database.db'
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.cfg')
    app.secret_key = 'secretkey'  # change later
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    mail.init_app(app)

    from .blueprints.auth import auth
    from .blueprints.views import views

    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(views, url_prefix="/")

    from .models import User, Note

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created database')

