from flask import Blueprint, render_template, request, flash, redirect, url_for
from .db_models import User, RSS_Data, User_Website_Link, User_Readlist_Link, Readlist, Tags, User_Interaction
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_login import login_user, login_required, logout_user, current_user
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

admin_dashboard = Blueprint('admin_dashboard', __name__)

class Admin_View(AdminIndexView):

    @expose('/')

    def index(self):
        activity = time_difference_calc()
        tags = Tags.query.all()

        global_tags_named = [tag.name for tag in tags]
        if current_user.id != 1:
            print(current_user)
            return redirect(url_for('views.home'))
        return self.render('admin/index.html', user_activity=activity, tags=global_tags_named)






def time_difference_calc():

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