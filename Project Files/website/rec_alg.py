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

def recommendation_algorithm():
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
    print(sorted_tag_clicks)
    for sorted_tag in sorted_tag_clicks:
        for tag in tags:

            if tag.id == sorted_tag:

                recommended_tags.append(sorted_tag)


    return recommended_tags







