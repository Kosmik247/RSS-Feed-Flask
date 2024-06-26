from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .db_models import User, RSS_Data, User_Website_Link, User_Readlist_Link, Readlist, User_Interaction
from .external_functions import valid_email

# ---- Blueprint Registration ---- #
auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """A function that is called when a user wants to log in to their account.

    Variables
    ----------
    email : str
        email to be checked from records
    password : str
        password to be checked against password associated with email supplied

    Returns
    -------
    User : Class object
          Returns user to home page if successful
          Returns user to login page if unsuccessful

    """
    # If user is already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        # If post request received from webpage, queries these specific variables from form
        email = request.form.get('email')
        password = request.form.get('password')

        # Checks for existence of user
        user = User.query.filter_by(email=email).first()

        # If user exists
        if user:
            # Hashes the input password and checks it against the hashed password stored in the database
            if check_password_hash(user.password, password):
                # If the hash matches, it logs the user in and caches the users login
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
                # If hash doesn't match, flags an error
            else:
                flash('Incorrect password, try again', category='error')
        # If user doesn't exist, flags an error to the user
        else:
            flash('Email does not exist', category='error')
    # If no post request, user remains on same webpage
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    """A function that is called when a user logs out (logs out of internal login manager).

    Variables
    ----------
    None

    Returns
    -------
    None: Returns user to login page

    """
    # Uses the flask_login "logout_user" function to log user out of the user login
    logout_user()

    # Returns the user to the login page
    return redirect(url_for('auth.login'))


@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """The profile function called when a user requests to go to their profile.

    Variables
    ----------
    password_1_n : str
        new password to be stored to the associated user
    password_2_n : str
        a verification variable to check password 1 is the correct password

    Returns
    -------
    User : Class object
        Returns user to profile page

    """
    if request.method == 'POST':
        # If post request received from user
        print(current_user.username)

        # Gets form inputs for password changes
        password_1_n = request.form.get('password_1')
        password_2_n = request.form.get('password_2')

        # If passwords don't match, doesn't change the password
        if password_1_n != password_2_n:
            flash('Passwords don\'t match', category='error')
        # If password does not match minimum parameters, doesn't change password
        elif len(password_1_n) < 5:
            flash('Password must be at least 5 characters', category='error')
        else:
            # Generates hash from new password and updates the user password
            current_user.password = generate_password_hash(password_1_n)
            db.session.commit()
            flash('Password Changed', category='success')

    # Returns user to profile page
    return render_template("profile.html", user=current_user)


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """The signup function called when a user creates an account.

    Variables
    ----------
    email : str
        email to be stored to associated user
    first_name : str
        name to be stored to associated user    
    password_1 : str
        password to be stored to associated user
    password_2 : str
        a verification variable to check password 1 is the correct password  
    new_user : str
        the new user to be added to the database if all checks run correctly

    Returns
    -------
    User : Class object
          Returns user to discover page if successful
          Returns user to signup page if unsuccessful

    """
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        # Retrieving form attributes
        email = request.form.get('email')
        username = request.form.get('username')
        password_1 = request.form.get('password_1')
        password_2 = request.form.get('password_2')

        user = User.query.filter_by(email=email).first()
        # Checks for each condition and flashes an error if condition true
        if user:
            flash('Email already exists', category='error')
        elif valid_email(email) is False:
            flash('Email is invalid', category='error')
        elif len(username) < 2:
            flash('Username must be greater than 2 characters', category='error')
        elif password_1 != password_2:
            flash('Passwords don\'t match', category='error')
        elif len(password_1) < 5:
            flash('Password must be at least 5 characters', category='error')
        else:
            # Creates a new user and adds the user to the database
            new_user = User(email=email, username=username, password=generate_password_hash(
                password_1))
            db.session.add(new_user)
            db.session.commit()
            # Uses Flask_Login to cache the user login and remember it if they closed and reopened the webpage
            login_user(new_user, remember=True)
            flash('Account created', category='success')
            return redirect(url_for('views.discover'))

    return render_template("sign_up.html", user=current_user)


@auth.route('/delete-account', methods=['POST'])
def delete_account():
    """The function that is called when a user wants to delete their account.

    Variables
    ----------
    user_id : int
        id of user who clicked the button
    user_websites : list of str
        A list of websites associated with the user
    user_articles : list of str
        A list of articles associated with the user
    del_user : str
        The current user held in temporary variable form

    Returns
    -------
    None : Returns user to login page

    """
    # Retrieves the uid fo the account
    user_id = request.form.get('account_id')

    # Retrieves all websites and articles that the user has saved (won't be stored when account is deleted)
    user_websites = User_Website_Link.query.filter_by(user_id=user_id).all()
    user_articles = User_Readlist_Link.query.filter_by(user_id=user_id).all()

    # If there is only one user with the article, it deletes the article
    for article in user_articles:
        article_existence = Readlist.query.get(article.readlist_id)
        if len(article_existence.users) == 1:
            db.session.delete(article_existence)
        db.session.delete(article)

    # If there is only one user with the website, it deletes the website (in case personal websites are added)
    for website in user_websites:
        website_existence = RSS_Data.query.get(website.rss_data_id)
        if len(website_existence.users) == 1:
            db.session.delete(website_existence)
        db.session.delete(website)

    # Retrieves all interactions built up by the user and deletes them
    user_interactions = User_Interaction.query.filter_by(user_id=current_user.id).all()
    for interaction in user_interactions:
        db.session.delete(interaction)

    # Logs user out and deletes user from database
    del_user = User.query.get(user_id)
    logout_user()

    db.session.delete(del_user)
    db.session.commit()
    # Redirects user to login page
    return redirect(url_for('auth.login'))
