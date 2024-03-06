from flask import Blueprint, redirect, url_for
from .db_models import Tags, User_Interaction

from datetime import timedelta
from flask_login import current_user
from flask_admin import AdminIndexView, expose

# Registers the blueprint within the flask application
admin_dashboard = Blueprint('admin_dashboard', __name__)

class Admin_View(AdminIndexView):

    @expose('/')

    def index(self):
        """The function behind the main index file in the flask admin view.

            Variables
            ----------
            activity : list of dates and activity\n
            tags : List of classes

            Returns
            -------
            returns user to admin page if admin
                    if user not admin, redirects user to homepage
        """
        # Obtains all activity for the dates and tags
        activity = time_difference_calc()
        tags = Tags.query.all()
        # Obtains the tag names from tags classes
        global_tags_named = [tag.name for tag in tags]
        # If the user is not the admin, return user to home page
        if current_user.id != 1:
            print(current_user)
            return redirect(url_for('views.home'))
        # Return user to the admin interface if admin
        return self.render('admin/index.html', user_activity=activity, tags=global_tags_named)






def time_difference_calc():
    """The function that calculates the difference in time between user interactions and their tags.
        Variables
        ----------
        activity_data : list of database entries\n
        global_activity : dict
        date : DateTime
        chart_data : list of lists
        date_dictionary : dict
        tags : list
        date_lol : list of list
        Returns
        -------
        returns date_lol
    """
    activity_data = User_Interaction.query.all()
    global_activity = {}
    for interaction in activity_data:
        date = interaction.time_of_interaction
        time_difference = date - timedelta(days=date.weekday())
        formatted_time = time_difference.strftime('%Y-%m-%d')

        if interaction.tag not in global_activity:
            global_activity[interaction.tag] = {'date': formatted_time, 'interactions': 1}
        else:
            global_activity[interaction.tag]['interactions'] += 1

    chart_data = [['Date', 'Interaction Count', 'Tag']]
    for data in global_activity:

        chart_data.append([global_activity[data]['date'], global_activity[data]['interactions'], data.name])

    date_dictionary = {}
    for data_list in chart_data[1:]:
        if data_list[0] not in date_dictionary:
            date_dictionary[data_list[0]] = [{data_list[2]: data_list[1]}]
        else:

            date_dictionary[data_list[0]].append({data_list[2]: data_list[1]})
    tags = list({tag for date_data in date_dictionary.values() for tag_dictionary in date_data for tag in tag_dictionary})

    # Create a list of lists with default values
    date_lol = [['Date'] + tags]

    for date, tag_data_list in date_dictionary.items():

        values = [0] * len(tags)

        for tag_data in tag_data_list:
            print(tag_data)
            for tag_name, value in tag_data.items():
                print(tag_name)
                print(value)
                values[tags.index(tag_name)] = value

        # Append the date and values to the result list
        date_lol.append([date] + values)

    print(date_lol)
    return date_lol