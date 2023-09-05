from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
import feedparser
from . import db
from .db_models import RSS_Data
views = Blueprint('views', __name__)

# Could use Jsonify as an alternative packaging tool for the returned information.
@views.route('/', methods=['GET','POST'])
@login_required
def home():
    website_link = 'None'

    if request.method == 'POST':
        website_title = request.form.get('feed_id')

        website = RSS_Data.query.filter_by(title=website_title).first()
        if website:
            website_link = website.link
            print(website_link)

        else:
            print("No websites stored in database.")
            website_link="None"

    feed = feedparser.parse(website_link)
    for article in feed['entries']:
        print(article.get("title"))
        print(article.get("description"))
        print(article.get("link"))

    return render_template("home.html", user=current_user, feeds=feed['entries'])


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        print(current_user.first_name)
        password_1_n = request.form.get('password_1')
        password_2_n = request.form.get('password_2')

        if password_1_n != password_2_n:
            flash('Passwords don\'t match.', category='error')

        elif len(password_1_n) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            current_user.password = generate_password_hash(password_1_n, method='sha256')
            db.session.commit()
            flash('Password Changed', category='success')
    return render_template("profile.html", user=current_user)

@views.route('/add_links', methods=['GET', 'POST'])
@login_required
def add_links():
    if request.method == 'POST':
        website_title = request.form.get('web_title')
        website_link = request.form.get('web_link')

        website_existence = RSS_Data.query.filter_by(title=website_title).first()
        if website_existence:
            flash('This title already exists', category='error')
        else:
            new_link = RSS_Data(title=website_title, link=website_link,user_id=current_user.id)
            db.session.add(new_link)
            db.session.commit()

    return render_template("website_add.html", user=current_user)


