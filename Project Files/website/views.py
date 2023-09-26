from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import feedparser
from . import db
from .db_models import RSS_Data

views = Blueprint('views', __name__)


# Could use Jsonify as an alternative packaging tool for the returned information.
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    website_link = 'None'

    if request.method == 'POST':
        if "feed_id" in request.form:
            website_title = request.form.get('feed_id')

            website = RSS_Data.query.filter_by(title=website_title).first()
            if website:
                website_link = website.link
                print(website_link)

            else:
                print("No websites stored in database.")
                website_link = "None"

        if "like_article" in request.form:
            value = request.form.get('value')
            print(value)
    feed = feedparser.parse(website_link)
    # for article in feed['entries']:
    #     print(article.get("title"))
    #     print(article.get("description"))
    #     print(article.get("link"))

    return render_template("home.html", user=current_user, feeds=feed['entries'])


@views.route('/delete-website', methods=['POST'])
@login_required
def delete_website():
    if request.method == 'POST':
        if "delete_link" in request.form:
            website_id = request.form.get('id')
            website = RSS_Data.query.get(website_id)
            if website:
                if website.user_id == current_user.id:
                    db.session.delete(website)
                    db.session.commit()
                    flash('Website deleted successfully', category='success')
            else:
                flash('Website not found', category='error')

    return render_template("home.html", user=current_user)


@views.route('/add_links', methods=['GET', 'POST'])
@login_required
def add_links():
    if request.method == 'POST':
        if "add_link" in request.form:
            website_title = request.form.get('web_title')
            website_link = request.form.get('web_link')

            website_existence = RSS_Data.query.filter_by(title=website_title).first()
            if website_existence and current_user.id == website_existence.user_id:
                flash('This title already exists', category='error')
            else:
                new_link = RSS_Data(title=website_title, link=website_link, user_id=current_user.id)
                db.session.add(new_link)
                db.session.commit()

    return render_template("website_add.html", user=current_user)
