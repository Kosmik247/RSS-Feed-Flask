from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
import feedparser
from . import db
from .db_models import RSS_Data
views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    feedURL = 'http://feeds.bbci.co.uk/news/health/rss.xml'
    feed = feedparser.parse(feedURL)


    for article in feed['entries']:
        print(article.get("title"))
        print(article.get("description"))
        print(article.get("link"))

    return render_template("home.html", user=current_user, feeds=feed['entries'], url=feedURL)


@views.route('/profile')
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@views.route('/add_website', methods=['POST'])
@login_required
def add_website():
    website_data = RSS_Data(link=request.form['website'], user_id=current_user.id)
    db.session.add(website_data)
    db.session.commit()
    return render_template("profile.html", user=current_user)