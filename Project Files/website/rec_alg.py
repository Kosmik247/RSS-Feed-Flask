from . import db
from .db_models import RSS_Data, Tags
import random
from flask_login import current_user
def test_alg():
    tag_clicks = {}
    tags = Tags.query.all()
    for tag in tags:
        tag_clicks[tag.id] = 0
    print(tag_clicks)
    # Query the database to retrieve all websites and all tags
    websites = RSS_Data.query.all()
    user_websites = [website for website in websites if website.user_id == current_user.id]
    print(user_websites)
    for website in user_websites:
        tag_clicks[website.tag_id] += website.clicks

    print(tag_clicks)






    ...


