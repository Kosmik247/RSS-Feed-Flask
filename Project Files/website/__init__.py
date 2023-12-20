from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager



db = SQLAlchemy()




def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sdadad hasdkjhsd akjhksdh'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///main_database.db'

    db.init_app(app)

    from .views import views
    from .auth import auth
    from .admin_dashboard_auth import admin_dashboard

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin_dashboard, url_prefix='/')


    from .db_models import User
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    return app


def create_database(app):
    if not path.exists('website/main_database.db'):
        db.create_all(app=app)
        print('Created Database!')

