from . import db
from datetime import datetime
from .db_models import RSS_Data, Tags, User_Interaction
import random
from flask_login import current_user
def weighted_calculation():
    """The function called when a user clicks on discover page. This function generates weightings based on the users interactions.

    Variables
    ----------
    tags : class
        list of global tags
    parse_weight : int
    save_weight : int
    recent_weight : int
    user_interactions : class
    tag_weights_calc : int
        The final tag weight calculated

    Returns
    -------
    tag_weights : dict
        A dictionary with the weight value assigned to each tag

    """
    tags = Tags.query.all()
    # --- Custom Weightings --- #
    parse_weight = 1
    save_weight = 2
    recent_weight = 0.8 # Decreases rating if it was recently interacted with

    user_interactions = User_Interaction.query.filter_by(user_id=current_user.id)

    # Defines tag_weights dictionary and sets the default weighting to 0 if there is no weight
    tag_weights = {tag: 0 for tag in tags}

    for interaction in user_interactions:
        # Defines weight based on the user interaction
        if interaction.interaction_type == "Parse":
            weight = parse_weight
        else:
            weight = save_weight

        # Calculating how recently the user interacted with the website
        time_difference = datetime.now() - interaction.time_of_interaction
        recent_factor = 1 / (1 + recent_weight * time_difference.total_seconds()) # Add another divider to decrease effect

        # Calculates weight for the tag
        tag_weights_calc = weight * recent_factor

        if interaction.tag in tag_weights:
            # Replaces the default of 0 with the tag weight calculated
            tag_weights[interaction.tag] += tag_weights_calc

    return tag_weights

def weighted_recommendation_algorithm():
    """The function behind the actual recommendation algorithm. It takes the weighting of each tag and selects 4
    random source websites to append to each tag. This recommends these 4 websites to the user.

    Variables
    ----------
    tag_weights : dict
        Tag weight values obtained from weighted_calculations()
    recommended_websites : dict
        dict of websites to return to the discover page function
    sorted_tags : dict
        Tag weight values but sorted via insertion
    tag_websites : class
        the list of websites related to the tag
    Returns
    -------
    recommended_websites : dict
        A dictionary containing all the recommended websites with their relevant tag as the dict key.

    """

    # Variable definition
    tag_weights = weighted_calculation()
    recommended_websites = {}
    # creates a list of the unsorted tags by their tag names (keys)
    tags_to_sort = list(tag_weights.keys())
    # puts tag list through the insertion sort function and returns the tags sorted
    sorted_tags = insertion_sort(tags_to_sort, tag_weights)

    for tag in sorted_tags:
        # Gets all the websites related to the tag
        tag_websites = RSS_Data.query.filter_by(tag_id=tag.id).all()

        # Since we do not want to modify database, we use a copy
        for website in tag_websites.copy():
            # Since each website is a dictionary, we define another category called articles and declare it empty
            website.__dict__['articles'] = {}

            # If any of the websites that the user has added are equal to this one, it removes the website from the copied list
            if any(user_websites.rss_data == website for user_websites in current_user.rss_data):
                tag_websites.remove(website)

        # Randomly shuffles the list of websites related to the tag and takes the first two to be displayed on the discover page
        # This limits the chance of a user seeing the same website recommended multiple times in a short span. (chance decreases the more websites I have)
        random.shuffle(tag_websites)
        if tag_websites:
            recommended_websites[tag] = tag_websites[:2] # Change number to change how many websites get shown on discover

    return recommended_websites

def insertion_sort(tags_to_sort,tag_weights):
    """The insertion sort function used to sort the tag_weights. Sorts tags by largest weighting first
    Parameters
    ----------
    tags_to_sort :
    tag_weights :

    Variables
    ----------
    current_tag : class

    Returns
    -------
    tags_to_sort : dict
         a dictionary of the tag classes, sorted by their weights

    """
    # Runs until there are no more tags to iterate over
    for i in range(len(tags_to_sort)):
        current_tag = tags_to_sort[i]

        j = i - 1
        # Checks to see if the current_tag is bigger than the tag in the current space
        while j >= 0 and tag_weights[current_tag] > tag_weights[tags_to_sort[j]]:
            # Shifts tag to the right to make space for the new bigger tag
            tags_to_sort[j + 1] = tags_to_sort[j]
            # If J reaches 0, it just appends tag at the end
            j -= 1
        # Appends the new big tag in the space
        tags_to_sort[j + 1] = current_tag

    return tags_to_sort

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


# ----- DEPRECATED -----#
# Below are older algorithms I used to both test the module and for other versions of the discovery algorithm to see how they performed.
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




