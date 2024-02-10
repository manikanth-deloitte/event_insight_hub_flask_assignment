from flask import render_template, redirect, request, url_for, abort, flash
from flask_login import login_user, login_required, logout_user

from . import db, app
from .model import User
from .forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash


@app.route('/')
def home():
    """
       Renders the home page.
    """

    return render_template("home.html")


@app.route('/welcome')
@login_required
def welcome():
    """
    Renders the welcome page for authenticated users.
    """
    return render_template('welcome.html')


@app.route('/logout')
@login_required
def logout():
    """
    Logs out the current user.
    """
    logout_user()
    flash('you logged out')
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
        Handle the user login, check the form data with database data
        for matching
    """
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Logged in successfully')
                next_welcome = request.args.get('next')
                if next_welcome or next_welcome[0] != '/':
                    next_welcome = url_for('welcome')
                return redirect(next_welcome)
        except Exception as e:
            flash(f"An Error occurred while logging in:{e}")
    return render_template('login.html', form=form, error="User doesn't Exit! -register")


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
     handles user registration by storing form data into the database
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            if User.query.filter_by(email=form.email.data).first():
                return render_template('register.html', form=form, error="Email already exists.")

            user = User(email=form.email.data,
                        username=form.username.data,
                        password=form.password.data,
                        phone_number=form.phone_number.data)
            db.session.add(user)
            db.session.commit()
            flash("Thanks for registration!")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"An error occurred while registering the user:{e}")
    return render_template('register.html', form=form)
