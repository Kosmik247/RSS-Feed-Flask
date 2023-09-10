from flask import Blueprint, render_template, request, flash, redirect, url_for
from .db_models import User, RSS_Data
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

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
        print(current_user.first_name)
        password_1_n = request.form.get('password_1')
        password_2_n = request.form.get('password_2')

        if password_1_n != password_2_n:
            flash('Passwords don\'t match.', category='error')

        elif len(password_1_n) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            current_user.password = generate_password_hash(password_1_n, method='sha256')
            db.session.commit()
            flash('Password Changed', category='success')
    return render_template("profile.html", user=current_user)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        password_1 = request.form.get('password_1')
        password_2 = request.form.get('password_2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password_1 != password_2:
            flash('Passwords don\'t match.', category='error')
        elif len(password_1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password_1, method='sha256'))
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
    user_websites = RSS_Data.query.filter_by(user_id=user_id).all()
    for website in user_websites:
        db.session.delete(website)
    db.session.commit()

    del_user = User.query.get(user_id)
    logout()

    db.session.delete(del_user)
    db.session.commit()

    return render_template("login.html", user=current_user)