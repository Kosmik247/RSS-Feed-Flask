from . import db
from datetime import datetime
from .db_models import RSS_Data, Tags, User_Interaction
import random
from flask_login import current_user
def test_alg():
    tag_clicks = {}
    tags = Tags.query.all()
    for tag in tags:
        tag_clicks[tag.id] = 0

    # Query the database to retrieve all websites and all tags
    websites = RSS_Data.query.all()
    user_websites = [website for website in websites if website.user_id == current_user.id]

    for website in user_websites:
        tag_clicks[website.tag_id] += website.clicks

    print(tag_clicks)
    ...
def tag_counter():
    """A function that tracks the number of clicks per tag,by building it up from all websites saved by the user"""
    tag_clicks = {}

    tags = Tags.query.all()
    for tag in tags:
        tag_clicks[tag.id] = 0

    user_websites = current_user.rss_data

    for website in user_websites:
        tag_clicks[website.rss_data.tag_id] += website.clicks

    # Sorts the dictionary that tracks count into numerical descending order and returns it
    sorted_tag_clicks = dict(sorted(tag_clicks.items(), key=lambda tag: tag[1], reverse=True))
    return sorted_tag_clicks

def global_tag_counter():
    """A function that tracks the number of clicks per tag,by building it up from all websites saved by the user"""
    tag_clicks = {}

    tags = Tags.query.all()
    for tag in tags:
        tag_clicks[tag.id] = 0

    # Query the database to retrieve all websites and all tags
    global_websites = RSS_Data.query.all()
    print(global_websites)

    for website in global_websites:
        for entry_link in website.users:
            print(entry_link.clicks)
            tag_clicks[website.tag_id] += entry_link.clicks

    # Sorts the dictionary that tracks count into numerical descending order and returns it
    sorted_tag_clicks = dict(sorted(tag_clicks.items(), key=lambda tag: tag[1], reverse=True))
    return sorted_tag_clicks
def top_interaction_recommendation_algorithm():
    """A popularity based recommendation system"""
    recommended_tags = []
    tags = Tags.query.all()
    sorted_tag_clicks = tag_counter()
    print(sorted_tag_clicks)
    for sorted_tag in sorted_tag_clicks:
        for tag in tags:

            if tag.id == sorted_tag:

                recommended_tags.append(sorted_tag)


    return recommended_tags

def weighted_calculation():
    """The calculation for the weights of each user interaction"""
def weighted_recommendation_algorithm():
    """The weighted algorithm for the recommendation system"""
    tags = Tags.query.all()
    # --- Custom Weightings --- #
    parse_weight = 1
    save_weight = 2
    recent_weight = 0.8
    diversity_weight = 0.5 # Diversity weighting to prevent same content from being re recommended. Varies with how wide the users interactions are and will keep a wider range recommended( Low weight rn cuase not many tags)

    user_interactions = User_Interaction.query.filter_by(user_id=current_user.id)
    unique_tags = []
    tag_weights = {}

    for interaction in user_interactions:
        # Initial weight definitions
        if interaction.interaction_type == "Parse":
            weight = parse_weight
        else:
            weight = save_weight

        # Calculating how recently the user interacted with the website
        time_difference = datetime.now() - interaction.time_of_interaction
        recent_factor = 1 / (1 + time_difference.total_seconds() / 3600)

        # Calculating the variety of tags
        for tag in tags:
            if tag.id == interaction.tag_id and tag not in unique_tags:
                unique_tags.append(tags[interaction.tag_id])

        diversity = 1/(1 + unique_tags * diversity_weight)
    print(unique_tags)
    pass





