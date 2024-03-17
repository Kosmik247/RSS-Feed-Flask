import feedparser
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from . import db
from .db_models import RSS_Data, Readlist, Tags, User_Website_Link, User_Readlist_Link, User_Interaction
from .external_functions import tag_counter, global_tag_counter, weighted_recommendation_algorithm

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    """A function that is called when a user wants to go to the home page.

        Variables
        ----------
        website_link : str
        website : class object
        user_tags : list
        global_tags : list of class objects
        user_saved_websites : list of class objects
        tags_format : dict
        website_id : int
        interaction : class object
        tag_id : int
        title : str
        description : str
        article_link : str
        existing_article : class object
        user_existing_article: bool
        new_user_entry : class object

        Returns
        -------
        user : Class object
                Returns user to home page
        tags : List of class objects
                Supplies homepage with the user tags
        feeds : Dictionary of class object
                Supplies homepage with user websites
        website : Class object
                RSS class object
    """
    # Initialisation of function variables to prevent errors
    website_link = 'None'
    website = None
    user_tags = []
    global_tags = Tags.query.all()
    user_saved_websites = current_user.rss_data

    # Checks every website to see what tags the user has added. Only adds the tags the user has selected to filter
    for user_web in user_saved_websites:
        tags_format = {'tag_id': user_web.rss_data.tag_id,
                       'tag_name': f'{global_tags[user_web.rss_data.tag_id].name}'}
        if tags_format not in user_tags:
            user_tags.append(tags_format)

    # If post method request to webpage
    if request.method == 'POST':
        website_id = request.form.get('website_id')

        # Every post request on home that has a website_id is counted as an interaction, which increments the click by 1
        website = User_Website_Link.query.filter_by(rss_data_id=website_id, user_id=current_user.id).first()
        website.clicks += 1

        # Checks the request.form for specific entries to enable different parts of the function
        if "feed_link" in request.form:
            # Creates an entry in the interaction table, with the type "parse" - NB: Different interactions have different types(see external functions for code)
            interaction = User_Interaction(user_id=current_user.id, tag_id=website.rss_data.tag_id,
                                           interaction_type="Parse")

            # Commits the interaction
            db.session.add(interaction)
            db.session.commit()

            website_link = website.rss_data.link
            # Finds the website from the link
            website = RSS_Data.query.filter_by(link=website_link).first()

        if "art_tag_id" in request.form:
            # Creates an interaction entry and obtains all the variables for the article
            interaction = User_Interaction(user_id=current_user.id, tag_id=website.rss_data.tag_id,
                                           interaction_type="Save")
            db.session.add(interaction)
            db.session.commit()

            # Pulls more parameters from webform and looks for an article
            tag_id = request.form.get('art_tag_id')
            title = request.form.get('article_title')
            description = request.form.get('article_desc')
            article_link = request.form.get('article_link')
            existing_article = Readlist.query.filter_by(art_title=title).first()

            # If article doesn't exist, creates an entry to the article database and saves it
            if not existing_article:
                tag_instance = Tags.query.get(tag_id)
                saved_article = Readlist(art_title=title, art_desc=description, art_link=article_link, tag=tag_instance)
                db.session.add(saved_article)
                db.session.commit()
                existing_article = saved_article
            user_existing_article = False

            # Checks if user has already saved the article
            for article in current_user.readlist:
                if article.readlist.art_title == title:
                    user_existing_article = True

            # If article not saved, links article to users
            if user_existing_article == False:
                new_user_entry = User_Readlist_Link(user_id=current_user.id, readlist_id=existing_article.id)
                db.session.add(new_user_entry)
                db.session.commit()
                flash('Article saved', category='success')

            # If article saved, flashes a warning
            elif user_existing_article == True:
                flash('Article already saved', category='error')

    feed = feedparser.parse(website_link)

    return render_template("home.html", user=current_user, feeds=feed['entries'], website=website, tags=user_tags)


@views.route('/delete-website', methods=['POST'])
@login_required
def delete_website():
    """A function that is called when a user wants to go to the home page.

        Variables
        ----------
        website_id : int
        link_table_website : Class object

        Returns
        -------
        None : Returns user to home
    """
    # If post request received
    if request.method == 'POST':

        # If delete link is in the form
        if "delete_link" in request.form:

            # Gets the existing link between the user and the website
            website_id = request.form.get('id')
            link_table_website = User_Website_Link.query.filter_by(rss_data_id=website_id,
                                                                   user_id=current_user.id).first()

            # If the website is linked to the user account
            if link_table_website:
                if link_table_website.user_id == current_user.id:
                    website = RSS_Data.query.get(website_id)

                    # Deletes the website if there is only the connection between user and website left
                    if len(website.users) == 1:
                        db.session.delete(website)

                    # Deletes link between the website and user
                    db.session.delete(link_table_website)
                    db.session.commit()
                    flash('Website deleted successfully', category='success')
            else:
                flash('Website not found', category='error')

    return redirect(url_for('views.home', run_path="/home"))


@views.route('/add_links', methods=['GET', 'POST'])
@login_required
def add_links():
    """A function that is called to add a new link.

        Variables
        ----------
        user_tags : list
        tags_list : list of classes
        website_title : string
        website_link : string
        website_tag : string

        Returns
        -------
        User : Class
            Returns user to website_add
        Tags : List
        User_tags : list
    """
    # Empty list to store the users tags
    user_tags = []
    tags_list = Tags.query.all()
    user_saved_websites = current_user.rss_data

    # Iterates through every website the user has saved
    for user_web in user_saved_websites:
        # Creates a dictionary website for each website
        tags_format = {'tag_id': user_web.rss_data.tag_id,
                       'tag_name': f'{tags_list[user_web.rss_data.tag_id].name}'}
        # Ensures that every tag the user has gets loaded, preventing duplicate tags
        if tags_format not in user_tags:
            user_tags.append(tags_format)

    # Post request from server
    if request.method == 'POST':
        # If the form contains add link
        if "add_link" in request.form:
            # Requests website data
            website_title = request.form.get('web_title')
            website_link = request.form.get('web_link')
            website_tag = request.form.get('web_tag')

            # Checks if website exists
            website_existence = RSS_Data.query.filter_by(title=website_title).first()

            # Checks if there is already a link between the website and the user
            try:
                website_link_existence = User_Website_Link.query.filter_by(user_id=current_user.id,
                                                                           rss_data_id=website_existence.id).first()
            # Sets the existence to false if website not found
            except AttributeError:
                website_link_existence = False

            # Error validation to ensure that the website isn't already linked to the account
            if website_existence and website_link_existence:
                flash('This title already exist | It\'s already linked to your account', category='error')

            # If the website exists in db, but the web-user link doesn't exist, creates a link and appends it to database
            elif website_existence and website_link_existence == None:
                new_website_link = User_Website_Link(user_id=current_user.id, rss_data_id=website_existence.id,
                                                     clicks=0)
                db.session.add(new_website_link)
                flash('This title has been added', category='success')

            # If the website isn't in db, adds website to db and creates link
            else:
                new_website = RSS_Data(title=website_title, link=website_link, tag_id=website_tag)
                db.session.add(new_website)
                db.session.commit()
                new_website_link = User_Website_Link(user_id=current_user.id, rss_data_id=new_website.id, clicks=0)
                db.session.add(new_website_link)
                flash('This title has been added', category='success')
            db.session.commit()

    # Returns user to html website template
    return render_template("website_add.html", user=current_user, tags=tags_list, user_tags=user_tags)


@views.route('/read_later', methods=['GET', 'POST'])
@login_required
def read_later():
    """Function behind the readlater/saved article page.

        Variables
        ----------
        user_tags : list
        global_tags : list of classes
        user_saved_articles : list of classes


        Returns
        -------
        User : Class
            Returns user to Readlater page
        Tags : List
        User_tags : list
    """
    # --- Tag Definition --- #
    # Gets all user tags related to the articles that the user has saved so that only those tags are presented to the user.
    user_tags = []
    global_tags = Tags.query.all()
    user_saved_articles = current_user.readlist

    # Creates a dictionary entry for every tag the user has saved
    for user_art in user_saved_articles:
        tags_format = {'tag_id': user_art.readlist.tag_id,
                       'tag_name': f'{global_tags[(user_art.readlist.tag_id)].name}'}

        # Appends the tag if it's not in list, preventing duplicate
        if tags_format not in user_tags:
            user_tags.append(tags_format)
    # Copy of tags list, allowing the filter category to act as an independent group
    title_tags = user_tags.copy()

    # --- POST METHOD --- #
    if request.method == 'POST':
        # --- Removes article that is saved from readlist --- #
        if "unlike_article" in request.form:
            article_id = request.form.get('unlike_article')
            article_to_del = Readlist.query.get(article_id)

            # Locates the link between user and article
            readlist_linktable_entry = User_Readlist_Link.query.filter_by(user_id=current_user.id,
                                                                          readlist_id=article_to_del.id).first()
            # Deletes link form database
            db.session.delete(readlist_linktable_entry)

            # If only one link exists, then it deletes the website
            if len(article_to_del.users) == 1:  # 0 value since the linked user is deleted beforehand, so it will have an empty associated list.
                db.session.delete(article_to_del)
            db.session.commit()
            flash('Article removed', category='success')

        # --- Refreshes the webpage with the relevant filters --- #
        # This if statement and its code works to remove the tag filtered from the filter_by bar, so other options are displayed
        if "filter_article" in request.form:
            tag_filter = request.form.get('filter_article')
            # Checks if data is not none
            if tag_filter != None:
                # Obtains the integer value of the tag id
                tag_filter = int(tag_filter)
                # Creates a dict entry with the specific filters
                dict_to_remove = {'tag_id': tag_filter, 'tag_name': f'{global_tags[tag_filter].name}'}
                # Indexes location of the tag that the user has selected to filter by
                index_of_dict = user_tags.index(dict_to_remove)
                # Deletes tag from the list so all other tags remain to be selected
                title_tags.pop(index_of_dict)
            user_tags = [{'tag_id': tag_filter, 'tag_name': f'{global_tags[tag_filter].name}'}]

    return render_template("read_later.html", user=current_user, tags=user_tags, filter_tags=title_tags)


@views.route('/discover', methods=['GET', 'POST'])
@login_required
def discover():
    """Function behind the discovery page.

        Variables
        ----------
        title : str
        link : str
        description : str
        tag_id : int
        articles : list


        Returns
        -------
        User : Class
        user_recommended_websites : List
        If website saved
            returns user to home page
        else
            returns user to discover page

    """
    # Runs discovery algorithm to retrieve tags in their weighted order
    user_recommended_websites = weighted_recommendation_algorithm()

    # --- Separation for all the POST method code --- #
    if request.method == 'POST':
        if "article_title" in request.form:
            title = request.form.get('article_title')
            # Checks if article is already saved
            existing_article = Readlist.query.filter_by(art_title=title).first()

            # try except to default the value to None if it doesn't exist
            try:
                readlist_link = User_Readlist_Link.query.filter_by(readlist_id=existing_article.id,
                                                                   user_id=current_user.id).first()
            except AttributeError:
                readlist_link = None
            # If statement that evaluates if article and readlist exists
            if existing_article and readlist_link:
                flash('Article already saved', category='error')
            # If article exists but no link exists
            elif existing_article and readlist_link == None:
                # Line that finds an existing article and adds it to the users articles.
                new_readlist_link = User_Readlist_Link(user_id=current_user.id, readlist_id=existing_article.id)
                db.session.add(new_readlist_link)
                flash('Article saved', category='success')
            else:
                # If neither article nor the link exist, create both
                link = request.form.get('article_link')
                description = request.form.get('article_desc')
                tag_id = request.form.get('tag_id')
                # Creates instance of article
                saved_article = Readlist(art_title=title, art_desc=description, art_link=link, tag_id=tag_id)
                db.session.add(saved_article)
                db.session.commit()
                new_readlist_link = User_Readlist_Link(user_id=current_user.id, readlist_id=saved_article.id)
                db.session.add(new_readlist_link)
                flash('Article saved', category='success')
            db.session.commit()

        # If statement to add to personal feed
        if "add_discovery_feed" in request.form:
            website_to_add = RSS_Data.query.filter_by(title=request.form.get('add_discovery_feed')).first()
            website_link_to_add = User_Website_Link(user_id=current_user.id, rss_data_id=website_to_add.id, clicks=0)
            db.session.add(website_link_to_add)
            db.session.commit()
            flash('Title added to home feed', category='success')
            return redirect(url_for('views.home', run_path="/home"))
        # If statement for filtering. This filtering only selects the tag, and to go back, all needs to be selected
        if "filter_websites" in request.form:
            user_desired_tag = request.form.get("filter_websites")
            relevant_tag = Tags.query.filter_by(name=user_desired_tag).first()
            if user_desired_tag == "None":
                user_recommended_websites = weighted_recommendation_algorithm()
            else:
                user_recommended_websites = {relevant_tag: user_recommended_websites[relevant_tag]}

    # --- END SEPARATION --- #
    for tag in user_recommended_websites:
        # For every website the user has been recommended
        for website in user_recommended_websites[tag]:
            # Uses feedparser to obtain the article links
            feed = feedparser.parse(website.link)
            # Selects the first 4 articles to show
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
    """Function behind the user_stats page.

        Variables
        ----------
        global_tags : list of classes
        global_tags_named : list of tag classes, named
        global_tags_id : list of tag classes, id
        stats_data : dict
        global_tag_clicks : dict


        Returns
        -------
        User : Class
            Returns user to stats page
        stats_data : dict
        global_tags : list
        named_tags : list
        id_tags : list
        websites : list
        global_clicks : dict
    """
    # Variables
    global_tags = Tags.query.all()
    global_tags_named = [tag.name for tag in global_tags]
    global_tags_id = [tag.id for tag in global_tags]
    stats_data = tag_counter()
    global_tag_clicks = global_tag_counter()
    # Limits the websites recommended to 4
    user_websites = User_Website_Link.query.filter_by(user_id=current_user.id).order_by(
        User_Website_Link.clicks.desc()).limit(4)
    print(current_user.rss_data)
    return render_template("user_stats.html", user=current_user, stats_data=stats_data, global_tags=global_tags,
                           named_tags=global_tags_named, id_tags=global_tags_id, websites=user_websites,
                           global_clicks=global_tag_clicks)
