from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


# Creating class User which inherits from DB.Model and Usermixin, a submodule of flask login. The Number found in
# db.string(x) is the maximum character limit.
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    date_signed_up = db.Column(db.DateTime(timezone=True), default=func.now())
    feeds = db.relationship('RSS_Data')
    liked = db.relationship('Readlist')


class RSS_Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10000))
    link = db.Column(db.String(10000))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    tag = db.Relationship('Tags', back_populates='website')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Readlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    art_title = db.Column(db.String(10000))
    art_desc = db.Column(db.String(10000))
    art_link = db.Column(db.String(10000))
    tag = db.Column(db.String(10000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10000))
    website = db.relationship('RSS_Data', back_populates='tag')


# class Visits(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     website_source = db.Column(db.string(10000))
#     visit_count = db.Column(db.Integer)
