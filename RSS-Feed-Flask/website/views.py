from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from .models import RSS_Data
from . import db
import feedparser

views = Blueprint('views', __name__)
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
   
    feedURL = 'http://feeds.bbci.co.uk/news/health/rss.xml'
    feed = feedparser.parse(feedURL)
    article = feed['entries']
  
    for article in feed['entries']:
        print(article.get("title"))
        print(article.get("description"))
        print(article.get("link"))

    return render_template("home.html", user=current_user, feeds=feed['entries'])

@views.route('/profile')
@login_required
def profile():
    

    return render_template("profile.html", user=current_user)