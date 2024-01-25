from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
# All database tables inherit from the basic class db.Model

# Link tables
class User_Website_Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rss_data_id = db.Column(db.Integer, db.ForeignKey('rss__data.id'))
    date_added = db.Column(db.DateTime(timezone=True), default=func.now())
    clicks = db.Column(db.Integer)
    # Define relationships to User and Website
    user = db.relationship('User', back_populates='rss_data')
    rss_data = db.relationship('RSS_Data', back_populates='users')

# Link tables
class User_Readlist_Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    readlist_id = db.Column(db.Integer, db.ForeignKey('readlist.id'))
    date_added = db.Column(db.DateTime(timezone=True), default=func.now())
    # Define relationships to User and Website
    user = db.relationship('User', back_populates='readlist')
    readlist = db.relationship('Readlist', back_populates='users')

# Defining User Table
# Usermixin is inherited by the user to allow the user class to use authentication parameters from the flask-login module
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    date_signed_up = db.Column(db.DateTime(timezone=True), default=func.now())
    # Define relationships
    rss_data = db.relationship('User_Website_Link', back_populates='user')
    readlist = db.relationship('User_Readlist_Link', back_populates='user')

# Defining Data Table
class RSS_Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10000))
    link = db.Column(db.String(10000))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    # Define relationships
    tag = db.relationship('Tags', back_populates='rss_data')
    users = db.relationship('User_Website_Link', back_populates='rss_data')


class Readlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    art_title = db.Column(db.String(10000))
    art_desc = db.Column(db.String(10000))
    art_link = db.Column(db.String(10000))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    # Define relationships
    tag = db.relationship('Tags', back_populates='readlist')
    users = db.relationship('User_Readlist_Link', back_populates='readlist')

class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10000))
    # Define relationships
    rss_data = db.relationship('RSS_Data', back_populates='tag')
    readlist = db.relationship('Readlist', back_populates='tag')
    user_interactions = db.relationship('User_Interaction', back_populates='tag')
class User_Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    interaction_type = db.Column(db.String(50))
    time_of_interaction = db.Column(db.DateTime(timezone=True), default=func.now())
    # Define relationships
    tag = db.relationship('Tags', back_populates='user_interactions')