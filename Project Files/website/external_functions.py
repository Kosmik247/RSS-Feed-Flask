from . import db
from datetime import datetime
from .db_models import RSS_Data, Tags, User_Interaction
import random
from flask_login import current_user
def weighted_calculation():
    """The calculation for the weights of each user interaction"""
    tags = Tags.query.all()
    # --- Custom Weightings --- #
    parse_weight = 1
    save_weight = 2
    recent_weight = 0.8

    user_interactions = User_Interaction.query.filter_by(user_id=current_user.id)

    tag_weights = {tag: 0 for tag in tags}

    for interaction in user_interactions:
        # Initial weight definitions
        if interaction.interaction_type == "Parse":
            weight = parse_weight
        else:
            weight = save_weight

        # Calculating how recently the user interacted with the website
        time_difference = datetime.now() - interaction.time_of_interaction
        recent_factor = 1 / (1 + recent_weight * time_difference.total_seconds()) # Add another divider to decrease effect

        tag_weights_calc = weight * recent_factor

        if interaction.tag in tag_weights:
            tag_weights[interaction.tag] += tag_weights_calc
    print(tag_weights)
    return tag_weights

def weighted_recommendation_algorithm():
    """The weighted algorithm for the recommendation system"""
    # print(weighted_calculation())
    tag_weights = weighted_calculation()
    recommended_websites = {}
    # Sort tags based on weighted popularity
    tags_to_sort = list(tag_weights.keys())
    # --------- REMOVE ---------- #
    #print(tags_to_sort)
    #sorted_tags = sorted(tag_weights.keys(), key=lambda tag: tag_weights[tag], reverse=True)
    #print(sorted_tags)
    sorted_tags = insertion_sort(tags_to_sort, tag_weights)

    for tag in sorted_tags:
        tag_websites = RSS_Data.query.filter_by(tag_id=tag.id).all()

        for website in tag_websites.copy():

            website.__dict__['articles'] = {}
            if any(user_websites.rss_data == website for user_websites in current_user.rss_data):

                tag_websites.remove(website)
        random.shuffle(tag_websites)
        if tag_websites:
            recommended_websites[tag] = tag_websites[:2] # Change number to change how many websites get shown on discover

    return recommended_websites

def insertion_sort(tags_to_sort,tag_weights):
    for i in range(len(tags_to_sort)):
        current_tag = tags_to_sort[i]

        j = i - 1
        while j >= 0 and tag_weights[current_tag] > tag_weights[tags_to_sort[j]]:

            tags_to_sort[j + 1] = tags_to_sort[j]
            j -= 1

        tags_to_sort[j + 1] = current_tag
    return tags_to_sort




# ----- DEPRECATED -----#
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




