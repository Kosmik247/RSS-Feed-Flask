from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
import feedparser
from . import db
from .db_models import RSS_Data, Readlist, Tags, User_Website_Link, User_Readlist_Link
from .rec_alg import recommendation_algorithm, tag_counter, global_tag_counter
views = Blueprint('views', __name__)


# Could use Jsonify as an alternative packaging tool for the returned information.
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():

    # recommendation_algorithm()
    website_link = 'None'
    website = None
    user_tags = []
    click_counts = []

    global_tags = Tags.query.all()

    user_saved_websites = current_user.rss_data

    for user_web in user_saved_websites:
        web_clicks = {'web_id': user_web.rss_data.id,
                      'click_count': user_web.clicks}
        click_counts.append(web_clicks)
        tags_format = {'tag_id': user_web.rss_data.tag_id,
                       'tag_name': f'{global_tags[user_web.rss_data.tag_id].name}'}
        if tags_format not in user_tags:
            user_tags.append(tags_format)


    if request.method == 'POST':
        website_id = request.form.get('website_id')

        live_click_dictionary = None
        for click_dictionary in click_counts:
            if click_dictionary['web_id'] == int(website_id):
                live_click_dictionary = click_dictionary
        website = User_Website_Link.query.filter_by(rss_data_id=website_id, user_id=current_user.id).first()
        website.clicks = int(live_click_dictionary['click_count']) + 1
        db.session.commit()

        if "feed_link" in request.form:
            website_link = request.form.get('feed_link')
            website = RSS_Data.query.filter_by(link=website_link).first()

            if website:
                website_link = website.link
            else:
                print("No websites stored in database.")
                website_link = "None"

        if "art_tag_id" in request.form:
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


    return render_template("home.html", user=current_user, feeds=feed['entries'], website=website, tags=user_tags, clicks=click_counts)


@views.route('/delete-website', methods=['POST'])
@login_required
def delete_website():
    if request.method == 'POST':
        if "delete_link" in request.form:
            website_id = request.form.get('id')
            link_table_website = User_Website_Link.query.filter_by(rss_data_id=website_id).first()
            print(link_table_website)
            if link_table_website:
                if link_table_website.user_id == current_user.id:
                    website = RSS_Data.query.get(website_id)
                    if len(website.users) == 1:
                        db.session.delete(website)

                    db.session.delete(link_table_website)


                    flash('Website deleted successfully', category='success')
            else:
                flash('Website not found', category='error')
        db.session.commit()
    return render_template("home.html", user=current_user)


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

            if len(article_to_del.users) == 0: # 0 value since the linked user is deleted beforehand, so it will have an empty associated list.
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
        ...
    return render_template("read_later.html", user=current_user, tags=user_tags)


@views.route('/discover', methods=['GET', 'POST'])
@login_required
def discover():
    # Runs discovery algorithm to prioritise tags
    user_recommended_tags = recommendation_algorithm()
    user_websites_sorted = []

    # --- Separation for all the POST method code --- #
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
            article_to_add = RSS_Data(title=request.form.get('add_discovery_feed'),
                                      link=request.form.get('source_link'), clicks=0, tag_id=request.form.get('source_tag'), user_id=current_user.id)
            db.session.add(article_to_add)
            db.session.commit()
        if "filter_websites" in request.form:
            user_desired_tag = request.form.get("filter_websites")
            if user_desired_tag == "None":
                user_recommended_tags = recommendation_algorithm()
            else:

                user_recommended_tags = [user_desired_tag]

    # --- END SEPARATION --- #
    global_websites = RSS_Data.query.all()

    for user_tag in user_recommended_tags:
        relevant_tag = Tags.query.filter_by(id=user_tag).first()
        individual_tag_groups = [[relevant_tag.id, relevant_tag.name]]

        for website in global_websites:
            # Checks if user has already added the website to their personal feed. IF they have, it does not appear.
            if website.user_id is None:
                website_existing = False
                for saved_website in current_user.rss_data:
                    if saved_website.title == website.title:
                        website_existing = True

            if website_existing != True:

                if website.tag_id == int(user_tag):

                    related_website = [f"{website.title}", f"{website.link}", f"{website.tag_id}"]
                    feed = feedparser.parse(website.link)
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

                        related_website.append(individual_articles_temp)
                    individual_tag_groups.append(related_website)

        if len(individual_tag_groups) != 1:
            user_websites_sorted.append(individual_tag_groups)
    return render_template("discover.html", user=current_user, discovery=user_websites_sorted)

@views.route('/user_stats', methods=['GET', 'POST'])
@login_required
def user_stats():
    """The function behind the user statistics page, it returns all required data."""
    global_tags = Tags.query.all()
    global_tags_named = [tag.name for tag in global_tags]
    global_tags_id = [tag.id for tag in global_tags]
    stats_data = tag_counter()
    global_tag_clicks = global_tag_counter()
    print(global_tag_clicks)
    user_websites = RSS_Data.query.filter_by(user_id=current_user.id).order_by(RSS_Data.clicks.desc()).limit(4)




    return render_template("user_stats.html", user=current_user, stats_data=stats_data,global_tags=global_tags, named_tags=global_tags_named, id_tags=global_tags_id, websites=user_websites, global_clicks=global_tag_clicks)