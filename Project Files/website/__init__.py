from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
import csv


db = SQLAlchemy()




def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sdadad hasdkjhsd akjhksdh'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///main_database.db'

    db.init_app(app)
    from .db_models import User, RSS_Data, User_Website_Link, Tags
    database_intialisation(app, User, RSS_Data, User_Website_Link, Tags)
    from .views import views
    from .auth import auth
    from .admin_dashboard_auth import admin_dashboard

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin_dashboard, url_prefix='/')





    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    return app


def database_intialisation(app, User, RSS_Data, User_Website_Link, Tags):

    with app.app_context():
        db.create_all()
        admin_user_existence = User.query.filter_by(email="sysadmin@gmail.com", username="sysadmin").first()
        if not admin_user_existence:
            admin_user = User(email="sysadmin@gmail.com", username="sysadmin", password=generate_password_hash(
                "1234567"))
            db.session.add(admin_user)
            db.session.commit()


            rss_csv_file_path = path.join(path.dirname(__file__), 'rss__data.csv')
            tags_csv_file_path = path.join(path.dirname(__file__), 'tags.csv')
            with open(tags_csv_file_path, 'r') as tag_file:
                tag_csvreader = csv.reader(tag_file)
                for row in tag_csvreader:
                    automatic_tag = Tags(id=row[0],name=row[1])
                    db.session.add(automatic_tag)

            with open(rss_csv_file_path, 'r') as rss_data_file:
                rss_data_csvreader = csv.reader(rss_data_file)
                for row in rss_data_csvreader:
                    automatic_rss_data = RSS_Data(title=row[1], link=row[2],tag_id=row[3])
                    db.session.add(automatic_rss_data)
            db.session.commit()

            websites = RSS_Data.query.all()
            for website in websites:
                default_user_link = User_Website_Link(user_id=admin_user.id, rss_data_id=website.id,clicks=0)
                db.session.add(default_user_link)
            db.session.commit()

