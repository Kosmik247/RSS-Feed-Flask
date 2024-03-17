# A copy of some of the database models from the website. The database here has been altered to experiment with
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(150), unique=True)
    password = Column(String(150))
    username = Column(String(150))
    date_signed_up = Column(DateTime(timezone=True), default=func.now())
    rss_data = relationship('User_Website_Link', back_populates='user')


class RSS_Data(Base):
    __tablename__ = 'rss_data'

    id = Column(Integer, primary_key=True)
    title = Column(String(10000))
    link = Column(String(10000))
    tag_id = Column(Integer, ForeignKey('tags.id'))
    tag = relationship('Tags', back_populates='rss_data')
    users = relationship('User_Website_Link', back_populates='rss_data')


class Tags(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(10000))
    rss_data = relationship('RSS_Data', back_populates='tag')


class User_Website_Link(Base):
    __tablename__ = 'user_website_link'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    rss_data_id = Column(Integer, ForeignKey('rss_data.id'))
    date_added = Column(DateTime(timezone=True), default=func.now())
    clicks = Column(Integer)
    user = relationship('User', back_populates='rss_data')
    rss_data = relationship('RSS_Data', back_populates='users')
