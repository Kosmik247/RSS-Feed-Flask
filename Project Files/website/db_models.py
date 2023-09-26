from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


# Creating class User which inherits from DB.Model and Usermixin, a submodule of flask login. The Number found in
# db.string(x) is the maximum character limit.
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    date_signed_up = db.Column(db.DateTime(timezone=True), default=func.now())
    feeds = db.relationship('RSS_Data')


class RSS_Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10000))
    link = db.Column(db.String(10000))
    liked = db.relationship('Readlist')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Readlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rss_data_id = db.Column(db.Integer, db.ForeignKey('rss__data.id'))
