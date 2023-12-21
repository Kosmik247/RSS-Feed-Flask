from flask import Blueprint, render_template, request, flash, redirect, url_for
from .db_models import User, RSS_Data, User_Website_Link, User_Readlist_Link, Readlist
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from flask_admin.contrib.sqla import ModelView
auth = Blueprint('auth', __name__)





@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        print(current_user.username)
        password_1_n = request.form.get('password_1')
        password_2_n = request.form.get('password_2')

        if password_1_n != password_2_n:
            flash('Passwords don\'t match.', category='error')

        elif len(password_1_n) < 5:
            flash('Password must be at least 5 characters.', category='error')
        else:
            current_user.password = generate_password_hash(password_1_n)
            db.session.commit()
            flash('Password Changed', category='success')
    return render_template("profile.html", user=current_user)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """A function that is called when a user wants to create an account.

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
    None: Returns user to home page

    """
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password_1 = request.form.get('password_1')
        password_2 = request.form.get('password_2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(username) < 2:
            flash('Username must be greater than 1 character.', category='error')
        elif password_1 != password_2:
            flash('Passwords don\'t match.', category='error')
        elif len(password_1) < 5:
            flash('Password must be at least 5 characters.', category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(
                password_1))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html",user=current_user)


@auth.route('/delete-account', methods=['POST'])
def delete_account():
    """A function that is called when a user wants to delete their account.

    Variables
    ----------
    user_id : int
        id of user who clicked the button

    user_websites : list of str
        A list of websites associated with the user

    del_user : str
        The current user held in temporary variable form
    Returns
    -------
    None: Returns user to login page

    """
    user_id = request.form.get('account_id')
    user_websites = User_Website_Link.query.filter_by(user_id=user_id).all()
    user_articles = User_Readlist_Link.query.filter_by(user_id=user_id).all()
    for article in user_articles:
        article_existence = Readlist.query.get(article.readlist_id)
        print(article_existence.users)
        if len(article_existence.users) == 1:
            db.session.delete(article_existence)
        db.session.delete(article)


    for website in user_websites:
        print(website)
        website_existence = RSS_Data.query.get(website.rss_data_id)
        print(website_existence.users)
        if len(website_existence.users) == 1:
            db.session.delete(website_existence)
        db.session.delete(website)

    del_user = User.query.get(user_id)
    logout()

    db.session.delete(del_user)
    db.session.commit()

    return render_template("login.html", user=current_user)

