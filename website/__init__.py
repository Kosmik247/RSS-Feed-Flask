from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
# ---- Init file for website module ---- #

# Initialises database class
db = SQLAlchemy()


def create_app():
    """The function that is run when the flask application is initialised

    Variables
    ----------
    app: class
        the flask application as a contained class

    Notes
    ----------
    This function initialises the application with all database models defined. It also registers
    all flask blueprints within the module for use as well as the files behind them.

    Returns
    -------
    app : class

    """

    # App initialisation with database configuration
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sdadad hasdkjhsd akjhksdh'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///main_database.db'

    db.init_app(app)
    # Import of all database models for program use and initialises it in the database
    from .db_models import User, RSS_Data, User_Website_Link, Tags
    database_intialisation(app)
    # Initialisation of each page index file as a blueprint
    from .views import views
    from .auth import auth
    from .admin_dashboard_auth import admin_dashboard

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin_dashboard, url_prefix='/')

    # Initialises the login manager for user ease and built in login system.
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


def database_intialisation(app):
    """The function run when the flask app is initialised.

    Variables
    ----------
    app : class
    db : class

    Returns
    -------
    None

    """

    with app.app_context():
        db.create_all()

