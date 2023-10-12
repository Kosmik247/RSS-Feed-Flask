from . import db
from .db_models import RSS_Data, Tags
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

def recommendation_algorithm(grouped_sorted_websites):
    """A popularity based recommendation system"""
    tag_clicks = {}
    recommended_tags = []
    tags = Tags.query.all()
    for tag in tags:
        tag_clicks[tag.id] = 0

    # Query the database to retrieve all websites and all tags
    websites = RSS_Data.query.all()
    user_websites = [website for website in websites if website.user_id == current_user.id]

    for website in user_websites:
        tag_clicks[website.tag_id] += website.clicks

    # Sorts the dictionary that tracks count into numerical descending order and returns it
    sorted_tag_clicks = dict(sorted(tag_clicks.items(), key=lambda tag: tag[1], reverse=True))

    for tag in tags:
        for sorted_tag in sorted_tag_clicks:
            if tag.id == sorted_tag:
                print("True")
                recommended_tags.append(tag.name,sorted_tag['tag.id'])

    print(recommended_tags)
    return sorted_tag_clicks







