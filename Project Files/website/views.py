from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import feedparser
from . import db
from .db_models import RSS_Data, Readlist, Tags

views = Blueprint('views', __name__)


# Could use Jsonify as an alternative packaging tool for the returned information.
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    website_link = 'None'
    website = None
    user_tags = []
    global_tags = Tags.query.all()
    user_saved_websites = RSS_Data.query.filter_by(user_id=current_user.id).all()
    for user_web in user_saved_websites:
        tags_format = {'tag_id': user_web.tag_id,
                       'tag_name': f'{global_tags[user_web.tag_id - 1].name}'}
        if tags_format not in user_tags:
            user_tags.append(tags_format)


    if request.method == 'POST':

        if "feed_id" in request.form:
            website_title = request.form.get('feed_id')
            website = RSS_Data.query.filter_by(title=website_title, user_id=current_user.id).first()

            if website:
                print(website)
                print(website.tag.name)
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
                tag_id = request.form.get('article_tag')
                print(tag_id)
                saved_article = Readlist(art_title=title, art_desc=description, art_link=link, tag=tag_id, user_id=current_user.id)
                db.session.add(saved_article)
                db.session.commit()

    feed = feedparser.parse(website_link)
    print(user_tags)

    return render_template("home.html", user=current_user, feeds=feed['entries'], website=website, tags=user_tags)


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
    tags_list = Tags.query.all()

    if request.method == 'POST':
        if "add_link" in request.form:
            website_title = request.form.get('web_title')
            website_link = request.form.get('web_link')
            website_tag = request.form.get('web_tag')
            print(website_tag)
            website_existence = RSS_Data.query.filter_by(title=website_title, user_id=current_user.id).first()
            if website_existence and current_user.id == website_existence.user_id:
                flash('This title already exists', category='error')
            else:
                new_link = RSS_Data(title=website_title, link=website_link, tag_id=website_tag, user_id=current_user.id)
                db.session.add(new_link)
                db.session.commit()

    return render_template("website_add.html", user=current_user, tags=tags_list)


@views.route('/read_later', methods=['GET', 'POST'])
@login_required
def read_later():
    if request.method == 'POST':
        if "unlike_article" in request.form:
            article_id = request.form.get('unlike_article')
            article_to_del = Readlist.query.get(article_id)
            db.session.delete(article_to_del)
            db.session.commit()
    return render_template("read_later.html", user=current_user)


@views.route('/discover', methods=['GET', 'POST'])
@login_required
def discover():
    if request.method == 'POST':
        if "article_title" in request.form:
            title = request.form.get('article_title')
            existing_article = Readlist.query.filter_by(art_title=title).first()
            if existing_article and existing_article.user_id == current_user.id:
                flash('Article already saved', category='error')
            else:

                link = request.form.get('article_link')
                description = request.form.get('article_desc')
                saved_article = Readlist(art_title=title, art_desc=description, art_link=link, user_id=current_user.id)
                db.session.add(saved_article)
                db.session.commit()

        if "add_discovery_feed" in request.form:
            title = request.form.get('add_discovery_feed')
            link = request.form.get('source_link')
            article_to_add = RSS_Data(title=request.form.get('add_discovery_feed'),
                                      link=request.form.get('source_link'),tag_id=request.form.get('source_tag'), user_id=current_user.id)
            db.session.add(article_to_add)
            db.session.commit()

    websites = RSS_Data.query.all()
    grouped_websites = []
    for website in websites:
        if website.user_id is None:
            website_existing = False
            for saved_website in current_user.feeds:

                if saved_website.title == website.title:
                    website_existing = True

            if website_existing != True:
                website_link = website.link
                related_articles = [f"{website.title}", f"{website_link}", f"{website.tag_id}"]
                feed = feedparser.parse(website_link)
                individual_articles = feed['entries'][0:4]
                # Stores individual articles as a dictionary in a list, this list is associated with its source link title
                for article in individual_articles:
                    # Try and except to catch out missing description discrepancies between sites
                    try:
                        individual_articles_temp = {'title': f'{article.title}', 'desc': f'{article.description}',
                                                    'link': f'{article.link}'}
                    except AttributeError:
                        individual_articles_temp = {'title': f'{article.title}',
                                                    'desc': f'No Description could be found for this article.',
                                                    'link': f'{article.link}'}
                    related_articles.append(individual_articles_temp)

                # Global grouped sources list that gets passed through to front end
                grouped_websites.append(related_articles)

            else:
                print("Website already saved and will not show in discover page")

    return render_template("discover.html", user=current_user, discovery=grouped_websites)
