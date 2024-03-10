# Main file run
# Module Imports
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from website import create_app  # Website Module
from website import db_models, db
from website.admin_dashboard_auth import Admin_View

# Initialises the app function in the website module
app = create_app()
# Initialises the different interface for the admin screen
admin = Admin(app, index_view=Admin_View())
admin.add_view(ModelView(db_models.User, db.session))
admin.add_view(ModelView(db_models.RSS_Data, db.session))
admin.add_view(ModelView(db_models.Tags, db.session))

# Runs file name __main__
if __name__ == '__main__':
    app.run('0.0.0.0', debug=True, port=8001)
