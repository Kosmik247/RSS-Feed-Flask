from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# All database tables inherit from the basic class db.Model
# Usermixin is inherited by the user to allow the user class to use authentication parameters

# Defining User Table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    date_signed_up = db.Column(db.DateTime(timezone=True), default=func.now())
    # Define relationships
    rss_data = db.relationship('User_Website_Link', back_populates='user')
    readlist = db.relationship('Readlist', back_populates='user')

# Defining Data Table
class RSS_Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10000))
    link = db.Column(db.String(10000))
    clicks = db.Column(db.Integer)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    # Define relationships
    tag = db.relationship('Tags', back_populates='rss_data')
    users = db.relationship('User', secondary='user_website_link', back_populates='rss_data')

class User_Website_Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rss_data_id = db.Column(db.Integer, db.ForeignKey('rss__data.id'))

    # Define relationships to User and Website
    user = db.relationship('User', back_populates='rss_data')
    rss_data = db.relationship('RSS_Data', back_populates='users')
class Readlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    art_title = db.Column(db.String(10000))
    art_desc = db.Column(db.String(10000))
    art_link = db.Column(db.String(10000))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))

    # Define relationships

    tag = db.relationship('Tags', back_populates='readlist')
    user = db.relationship('User', back_populates='readlist')

class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10000))
    # Define relationships
    rss_data = db.relationship('RSS_Data', back_populates='tag')
    readlist = db.relationship('Readlist', back_populates='tag')

