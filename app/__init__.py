from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor


db = SQLAlchemy()

def create_app():
    # App Initializing
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "a"

    bootstrap = Bootstrap(app)
    ckeditor = CKEditor(app)
    
    # Views and Auth Initializing
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth/")

    # Database Initializing
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    db.init_app(app)

    from .models import User
    create_database(app)

    # Flask Login Initializing
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)
    # Load User by its Username (Primary Key)
    @login_manager.user_loader
    def load_user(username):
        return User.query.get(username)
    

    return app


def create_database(app):
    if not path.exists("app/database.db"):
        with app.app_context():
            db.create_all()
        