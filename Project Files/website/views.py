from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
import feedparser
from . import db
from .db_models import RSS_Data, Readlist, Tags, User_Website_Link, User_Readlist_Link, User_Interaction
from .external_functions import top_interaction_recommendation_algorithm, tag_counter, global_tag_counter, weighted_recommendation_algorithm
views = Blueprint('views', __name__)


# Could use Jsonify as an alternative packaging tool for the returned information.
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():


    website_link = 'None'
    website = None
    user_tags = []

    global_tags = Tags.query.all()

    user_saved_websites = current_user.rss_data

    for user_web in user_saved_websites:

        tags_format = {'tag_id': user_web.rss_data.tag_id,
                       'tag_name': f'{global_tags[user_web.rss_data.tag_id].name}'}
        if tags_format not in user_tags:
            user_tags.append(tags_format)


    if request.method == 'POST':
        website_id = request.form.get('website_id')


        website = User_Website_Link.query.filter_by(rss_data_id=website_id, user_id=current_user.id).first()
        website.clicks += 1

        if "feed_link" in request.form:

            interaction = User_Interaction(user_id=current_user.id,tag_id=website.rss_data.tag_id,interaction_type="Parse")

            db.session.add(interaction)
            db.session.commit()
            website_link = website.rss_data.link


            website = RSS_Data.query.filter_by(link=website_link).first()


        if "art_tag_id" in request.form:
            interaction = User_Interaction(user_id=current_user.id, tag_id=website.rss_data.tag_id,interaction_type="Save")
            db.session.add(interaction)
            db.session.commit()
            tag_id = request.form.get('art_tag_id')
            title = request.form.get('article_title')
            description = request.form.get('article_desc')
            article_link = request.form.get('article_link')


            existing_article = Readlist.query.filter_by(art_title=title).first()

            if not existing_article:
                tag_instance = Tags.query.get(tag_id)
                saved_article = Readlist(art_title=title, art_desc=description, art_link=article_link, tag=tag_instance)
                db.session.add(saved_article)
                db.session.commit()
                existing_article = saved_article
            user_existing_article = False
            for article in current_user.readlist:
                if article.readlist.art_title == title:
                    user_existing_article = True
            if user_existing_article == False:
                new_user_entry = User_Readlist_Link(user_id=current_user.id, readlist_id=existing_article.id)
                db.session.add(new_user_entry)
                db.session.commit()
            elif user_existing_article == True:
                flash('Article already saved', category='error')


    feed = feedparser.parse(website_link)


    return render_template("home.html", user=current_user, feeds=feed['entries'], website=website, tags=user_tags)


@views.route('/delete-website', methods=['POST'])
@login_required
def delete_website():
    if request.method == 'POST':
        if "delete_link" in request.form:
            website_id = request.form.get('id')
            link_table_website = User_Website_Link.query.filter_by(rss_data_id=website_id, user_id=current_user.id).first()
            print(link_table_website)
            if link_table_website:
                if link_table_website.user_id == current_user.id:
                    website = RSS_Data.query.get(website_id)
                    if len(website.users) == 1:
                        db.session.delete(website)

                    db.session.delete(link_table_website)

                    db.session.commit()
                    flash('Website deleted successfully', category='success')
            else:
                flash('Website not found', category='error')

    return redirect(url_for('views.home',run_path="/home"))


@views.route('/add_links', methods=['GET', 'POST'])
@login_required
def add_links():
    user_tags = []

    tags_list = Tags.query.all()
    user_saved_websites = current_user.rss_data

    for user_web in user_saved_websites:

        tags_format = {'tag_id': user_web.rss_data.tag_id,
                       'tag_name': f'{tags_list[user_web.rss_data.tag_id].name}'}
        if tags_format not in user_tags:
            user_tags.append(tags_format)


    if request.method == 'POST':
        if "add_link" in request.form:
            website_title = request.form.get('web_title')
            website_link = request.form.get('web_link')
            website_tag = request.form.get('web_tag')
            print(website_tag)

            website_existence = RSS_Data.query.filter_by(title=website_title).first()

            try:
                website_link_existence = User_Website_Link.query.filter_by(user_id=current_user.id, rss_data_id=website_existence.id).first()
            except AttributeError:
                website_link_existence = False


            if website_existence and website_link_existence:
                flash('This title already exist | It\'s already linked to your account', category='error')
            elif website_existence and website_link_existence == None:
                new_website_link = User_Website_Link(user_id=current_user.id, rss_data_id=website_existence.id, clicks=0)
                db.session.add(new_website_link)
                flash('This title has been added', category='success')
            else:
                new_website = RSS_Data(title=website_title, link=website_link, tag_id=website_tag)
                db.session.add(new_website)
                db.session.commit()
                new_website_link = User_Website_Link(user_id=current_user.id, rss_data_id=new_website.id, clicks=0)
                db.session.add(new_website_link)
            db.session.commit()


    return render_template("website_add.html", user=current_user, tags=tags_list, user_tags=user_tags)


@views.route('/read_later', methods=['GET', 'POST'])
@login_required
def read_later():
    """Function behind the readlater/saved article page."""
    # --- Tag Definition --- #
    # Gets all user tags related to the articles that the user has saved so that only those tags are presented to the user.
    user_tags = []
    global_tags = Tags.query.all()
    user_saved_articles = current_user.readlist
    for user_art in user_saved_articles:
        tags_format = {'tag_id': user_art.readlist.tag_id,
                       'tag_name': f'{global_tags[(user_art.readlist.tag_id)].name}'}
        if tags_format not in user_tags:
            user_tags.append(tags_format)
    #--- POST METHOD --- #
    if request.method == 'POST':
        # --- Removes article that is saved from readlist --- #
        if "unlike_article" in request.form:
            article_id = request.form.get('unlike_article')
            article_to_del = Readlist.query.get(article_id)

            readlist_linktable_entry = User_Readlist_Link.query.filter_by(user_id=current_user.id, readlist_id=article_to_del.id).first()
            print(article_to_del.users)
            db.session.delete(readlist_linktable_entry)

            if len(article_to_del.users) == 1: # 0 value since the linked user is deleted beforehand, so it will have an empty associated list.
                db.session.delete(article_to_del)
            db.session.commit()

        # --- Refreshes the webpage with the relevant filters --- #
        if "filter_article" in request.form:
            tag_filter = request.form.get('filter_article')
            if tag_filter != None:
                tag_filter = int(tag_filter)

            user_tags = [{'tag_id': tag_filter,
                          'tag_name': f'{global_tags[tag_filter-1].name}'}]
            print(user_tags)

    return render_template("read_later.html", user=current_user, tags=user_tags)


@views.route('/discover', methods=['GET', 'POST'])
@login_required
def discover():
    # Runs discovery algorithm to prioritise tags

    user_recommended_websites = weighted_recommendation_algorithm()


    # --- Separation for all the POST method code --- #
    if request.method == 'POST':
        if "article_title" in request.form:
            title = request.form.get('article_title')
            existing_article = Readlist.query.filter_by(art_title=title).first()
            print(existing_article)
            try:
                readlist_link = User_Readlist_Link.query.filter_by(readlist_id=existing_article.id, user_id=current_user.id).first()
            except AttributeError:
                readlist_link = None
            print(readlist_link)
            if existing_article and readlist_link:
                # If statement that evaluates if article and readlist exists
                print("True")
                flash('Article already saved', category='error')
            elif existing_article and readlist_link == None:
                print(True)
                # Function that finds an existing article and adds it to the users articles.
                new_readlist_link = User_Readlist_Link(user_id=current_user.id, readlist_id=existing_article.id)
                db.session.add(new_readlist_link)
                flash('Article saved', category='success')
            else:

                link = request.form.get('article_link')
                description = request.form.get('article_desc')
                tag_id = request.form.get('tag_id')
                saved_article = Readlist(art_title=title, art_desc=description, art_link=link, tag_id=tag_id)
                db.session.add(saved_article)
                db.session.commit()
                new_readlist_link = User_Readlist_Link(user_id=current_user.id, readlist_id=saved_article.id)
                db.session.add(new_readlist_link)
                flash('Article saved', category='success')
            db.session.commit()

        if "add_discovery_feed" in request.form:
            website_to_add = RSS_Data.query.filter_by(title=request.form.get('add_discovery_feed')).first()
            website_link_to_add = User_Website_Link(user_id=current_user.id, rss_data_id=website_to_add.id, clicks=0)
            db.session.add(website_link_to_add)
            db.session.commit()
            return redirect(url_for('views.home',run_path="/home"))

        if "filter_websites" in request.form:
            user_desired_tag = request.form.get("filter_websites")
            relevant_tag = Tags.query.filter_by(name=user_desired_tag).first()
            if user_desired_tag == "None":
                user_recommended_websites = weighted_recommendation_algorithm()
            else:
                print(user_recommended_websites[relevant_tag])
                user_recommended_websites = {relevant_tag : user_recommended_websites[relevant_tag]}


    # --- END SEPARATION --- #
    for tag in user_recommended_websites:
        for website in user_recommended_websites[tag]:
            feed = feedparser.parse(website.link)
            individual_articles = feed['entries'][0:4]
            articles = []
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
                articles.append(individual_articles_temp)
            website.articles = articles




    return render_template("discover.html", user=current_user, discovery=user_recommended_websites)

@views.route('/user_stats', methods=['GET', 'POST'])
@login_required
def user_stats():
    """The function behind the user statistics page, it returns all required data."""
    global_tags = Tags.query.all()
    global_tags_named = [tag.name for tag in global_tags]
    global_tags_id = [tag.id for tag in global_tags]
    stats_data = tag_counter()
    global_tag_clicks = global_tag_counter()
    user_websites = User_Website_Link.query.filter_by(user_id=current_user.id).order_by(User_Website_Link.clicks.desc()).limit(4)



    return render_template("user_stats.html", user=current_user, stats_data=stats_data,global_tags=global_tags, named_tags=global_tags_named, id_tags=global_tags_id, websites=user_websites, global_clicks=global_tag_clicks)