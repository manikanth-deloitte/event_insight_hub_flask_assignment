from flask import render_template, redirect, request, url_for, abort, flash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect
from . import db, app
from .model import User, Event, Feedback
from .forms import LoginForm, RegistrationForm, EventOrganizerForm, UpdateEventForm
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
    message = None
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Logged in successfully')
                next_welcome = request.args.get('next')
                if next_welcome is None or next_welcome[0] != '/':
                    next_welcome = url_for('welcome')
                return redirect(next_welcome)
            else:
                message = "User doesn't Exit! -register"
        except Exception as e:
            flash(f"An Error occurred while logging in:{e}")
    return render_template('login.html', form=form, error=message)


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


@app.route('/organize', methods=['GET', 'POST'])
def organize_event():
    form = EventOrganizerForm()
    if form.validate_on_submit():
        if Event.query.filter_by(name=form.name.data).first():
            return render_template('organizer.html', form=form,
                                   error="Event with this name already exists!")
        event = Event(
            name=form.name.data,
            description=form.description.data,
            datetime=form.datetime.data,
            location=form.location.data,
            organizer_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Event organized successfully!', 'success')
        return redirect(url_for('events'))  # Redirect to the home page after organizing the event
    return render_template('organizer.html', form=form)


@app.route('/events', methods=['GET', 'POST'])
def events():
    return render_template('events.html')


@app.route('/all_events', methods=['GET', 'POST'])
def all_events():
    all_events = Event.query.all()
    return render_template('all_events.html', events=all_events)


# @app.route('/events_paticipated', methods=['GET', 'POST'])
# def registered_events():
#     all_events = Event.query.all()
#     return render_template('events_participated.html', events=all_events)
#
# @app.route('/organized_events', methods=['GET', 'POST'])
# def organized_events():
#     all_events = Event.query.all()
#     return render_template('organised_events.html', events=all_events)


@app.route('/event_details/<event_id>')
def event_details(event_id):
    # Retrieve the event from the database using the event_id
    event = Event.query.get(event_id)
    if not event:
        abort(404)  # Return a 404 error if the event is not found
    return render_template('event_details.html', event=event)


@app.route('/register/<event_id>', methods=['POST'])
def register_event(event_id):
    event = Event.query.get(event_id)

    user = User.query.get(current_user.id)

    # Check if the user is already registered for the event
    if user in event.participants:
        flash('You are already registered for this event!', 'info')
        return redirect(url_for('events'))  # Redirect to events page

    # Add the user to the event's participants list
    event.participants.append(user)

    # Commit the changes to the database
    db.session.commit()

    flash('Successfully registered for the event!', 'success')
    return redirect(url_for('events'))


@app.route('/events/events_registered', methods=['GET'])
@login_required
def user_registered_events():
    user = current_user  # Assuming the current user is authenticated
    registered_events = Event.query.filter(Event.participants.any(id=user.id)).all()
    return render_template('events_participated.html', events=registered_events)


@app.route('/events/organized_events', methods=['GET'])
@login_required
def user_organized_events():
    # Get the current user's organized events
    organized_events = current_user.organized_events
    # Render the organized_events.html template and pass the events to it
    return render_template('organized_events.html', events=organized_events)

# @app.route('/event/update_form', methods=['GET'])
# def click_update_event():
#     return render_template('update_event.html')
#

@app.route('/event/update/<event_id>', methods=['GET', 'POST'])
def update_event(event_id):
    event = Event.query.get(event_id)
    form = UpdateEventForm(obj=event)  # Pass the event object to populate the form
    if form.validate_on_submit():
        # Update the event details based on the form data
        event.name = form.name.data
        event.description = form.description.data
        event.datetime = form.datetime.data
        event.location = form.location.data
        db.session.commit()
        flash('Event details updated successfully!', 'success')
        return redirect(url_for('user_organized_events'))
    return render_template('update_event.html', form=form, event=event)


@app.route('/event/delete/<event_id>', methods=['POST'])
def delete_event(event_id):
    # Retrieve the event from the database
    event = Event.query.get(event_id)
    if event:
        # Delete the event
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully', 'success')
        return redirect(url_for('user_organized_events'))
    else:
        flash('Event not found', 'error')
    return redirect(url_for('user_organized_events'))
