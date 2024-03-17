import csv
from os import path

from werkzeug.security import generate_password_hash

from website import create_app
from website import db
from website.db_models import User, Tags, User_Website_Link, RSS_Data

app = create_app()


def database_intialisation():
    """When this function is run, it creates the database, adds testing data and creates a test admin account"""

    with app.app_context():
        db.create_all()
        # Checks if admin user account details exists
        admin_user_existence = User.query.filter_by(email="sysadmin@gmail.com", username="sysadmin").first()

        # If admin account has not been made, it creates the account and runs the rest of the creation program.
        if not admin_user_existence:

            # Creates user instance and adds it to the database
            # ---- NOTE ---- # ADMIN PASSWORD IS HARD CODED: REPLACE 1234567 WITH PASSWORD DESIRED - OR FIRST ACCOUNT CREATED
            admin_user = User(email="sysadmin@gmail.com", username="sysadmin", password=generate_password_hash(
                "1234567"))
            db.session.add(admin_user)
            db.session.commit()

            # Locates relative path to the rss and tags file
            rss_csv_file_path = path.join(path.dirname(__file__), '../Testing/rss__data.csv')
            tags_csv_file_path = path.join(path.dirname(__file__), '../Testing/tags.csv')
            # Opens the tags.csv and loops through, automatically adding each one to the database
            with open(tags_csv_file_path, 'r') as tag_file:
                tag_csvreader = csv.reader(tag_file)
                for row in tag_csvreader:
                    automatic_tag = Tags(id=row[0], name=row[1])
                    db.session.add(automatic_tag)

            # Opens the RSS_Data csv and loops through, automatically adding each website ("default dataset") to the database
            with open(rss_csv_file_path, 'r') as rss_data_file:
                rss_data_csvreader = csv.reader(rss_data_file)
                for row in rss_data_csvreader:
                    automatic_rss_data = RSS_Data(title=row[1], link=row[2], tag_id=row[3])
                    db.session.add(automatic_rss_data)
            db.session.commit()

            # Gets websites from database and automatically links every one to the admin account to prevent them from being deleted
            websites = RSS_Data.query.all()
            for website in websites:
                default_user_link = User_Website_Link(user_id=admin_user.id, rss_data_id=website.id, clicks=0)
                db.session.add(default_user_link)
            db.session.commit()


database_intialisation()
