from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import feedparser
from . import db
from .db_models import RSS_Data, Readlist

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

        if "article_title" in request.form:
            title = request.form.get('article_title')
            website_link = request.form.get('source_link')
            existing_article = Readlist.query.filter_by(art_title=title).first()
            if existing_article and existing_article.user_id == current_user.id:
                flash('Article already saved', category='error')
            else:

                link = request.form.get('article_link')
                description = request.form.get('article_desc')
                saved_article = Readlist(art_title=title, art_desc=description, art_link=link, user_id=current_user.id)
                db.session.add(saved_article)
                db.session.commit()



    feed = feedparser.parse(website_link)


    return render_template("home.html", user=current_user, feeds=feed['entries'], website=website_link)


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

@views.route('/read_later', methods=['GET','POST'])
@login_required
def read_later():
    if request.method == 'POST':
        if "unlike_article" in request.form:
            article_id = request.form.get('unlike_article')
            article_to_del = Readlist.query.get(article_id)
            db.session.delete(article_to_del)
            db.session.commit()
    return render_template("read_later.html", user=current_user)