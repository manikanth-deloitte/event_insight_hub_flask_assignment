from datetime import timedelta, datetime
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from . import db, app
from .model import User, Event, Feedback
from .forms import LoginForm, RegistrationForm, EventOrganizerForm, UpdateEventForm, EventFeedbackForm
from .analytics_dashboard import generate_graph


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


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
@login_required
def organize_event():
    """
        This function will get the data from organize form and store to event data base
    """
    form = EventOrganizerForm()
    if form.validate_on_submit():
        try:
            if Event.query.filter_by(name=form.name.data).first():
                return render_template('organizer.html', form=form,
                                       error="Event with this name already exists!")
            # save it to event database
            event = Event(
                name=form.name.data,
                description=form.description.data,
                date_time=form.date_time.data,
                event_duration=form.duration.data,
                location=form.location.data,
                organizer_id=current_user.id
            )
            db.session.add(event)
            db.session.commit()
            flash('Event organized successfully!', 'success')
            return redirect(url_for('user_organized_events'))
        except Exception as e:
            flash(f"error generated while  organise data saving to Event DB {e}")
    return render_template('organizer.html', form=form)


@app.route('/events', methods=['GET'])
@login_required
def events():
    """
        This function render to list of categorize events
    """
    return render_template('events.html')


@app.route('/all_events', methods=['GET', 'POST'])
@login_required
def all_events():
    """
    This function will get the all the event details
    """
    all_events = Event.query.all()
    return render_template('all_events.html', events=all_events, title="EVENTS LIST")


@app.route('/event_details/<event_id>')
@login_required
def event_details(event_id):
    """
    This function get the event based and show status of registration
    based on time/already registered/organizer
    """
    event = Event.query.get(event_id)

    # check if participant is organiser
    user = User.query.get(current_user.id)
    organiser = False
    if user.id == event.organizer_id:
        organiser = True

    # check if user is already registered
    events_list = Event.query.filter(Event.participants.any(id=user.id)).all()
    registered = False
    for participated_event in events_list:
        if participated_event.id == event.id:
            registered = True

    # check for the scheduled time
    event_closed = False
    current_date = datetime.now()
    if current_date >= event.date_time:
        event_closed = True

    return render_template('event_details.html', event=event, event_closed=event_closed,
                           registered=registered, organiser=organiser)


@app.route('/register/<event_id>', methods=['POST'])
def register_event(event_id):
    """
    This function will add the participant to event DB when user registered
    """
    event = Event.query.get(event_id)

    user = User.query.get(current_user.id)

    # Check if the user is already registered for the event
    if user in event.participants:
        flash('You are already registered for this event!')
        return redirect(url_for('user_registered_events'))

    event.participants.append(user)
    db.session.commit()

    flash('Successfully registered for the event!')
    return redirect(url_for('user_registered_events'))


@app.route('/events/events_registered', methods=['GET'])
@login_required
def user_registered_events():
    """
    This function will get the user specific registered events
    """
    user = current_user  # Assuming the current user is authenticated
    events_list = Event.query.filter(Event.participants.any(id=user.id)).all()

    current_date = datetime.now()
    registered_events_list = [event for event in events_list if event.date_time > current_date]

    return render_template('events_participated.html', events=registered_events_list, title="REGISTERED EVENTS")


@app.route('/events/events_participated', methods=['GET'])
@login_required
def user_participated_events():
    """
    This function will get the user participated events , the event user
    registered and participated(event time completed)
    """
    user = current_user
    events_list = Event.query.filter(Event.participants.any(id=user.id)).all()

    # check event time is completed
    current_date = datetime.now()
    participated_events_list = [event for event in events_list if
                                event.date_time + timedelta(minutes=int(event.duration)) < current_date]

    return render_template('events_participated.html', events=participated_events_list, title="PARTICIPATED EVENTS",
                           feedback_button=True)


@app.route('/events/organized_events', methods=['GET'])
@login_required
def user_organized_events():
    """
    This function will get the user organized events and display event details
    """
    organized_events = current_user.organized_events
    return render_template('organized_events.html', events=organized_events)


@app.route('/archived_events', methods=['GET'])
def archived_events():
    events_list = Event.query.all()

    # events that are completed
    current_date = datetime.now()
    archived_events_list = [event for event in events_list if
                            event.date_time + timedelta(minutes=int(event.duration)) <= current_date]

    return render_template('all_events.html', events=archived_events_list, title="ARCHIVED EVENTS ")


@app.route('/event/update/<event_id>', methods=['GET', 'POST'])
def update_event(event_id):
    """
        This function will update the event details
    """
    event = Event.query.get(event_id)
    form = UpdateEventForm(obj=event)
    if form.validate_on_submit():
        try:
            event.name = form.name.data
            event.description = form.description.data
            event.date_time = form.date_time.data
            event.duration = form.duration.data
            event.location = form.location.data
            db.session.commit()
            flash('Event details updated successfully!')
            return redirect(url_for('user_organized_events'))
        except Exception as e:
            flash(f"Error occurred when saving updated event details to database {e}")
    return render_template('update_event.html', form=form, event=event)


@app.route('/event/delete/<event_id>', methods=['POST'])
def delete_event(event_id):
    """
    This function will delete the even from DB
    """
    event = Event.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully', 'success')
        return redirect(url_for('user_organized_events'))
    else:
        flash('Event not found', 'error')
    return redirect(url_for('user_organized_events'))


@app.route('/events/<event_id>/feedback', methods=['GET', 'POST'])
def show_feedback_form(event_id):
    event = Event.query.get(event_id)
    form = EventFeedbackForm()
    return render_template('feedback_form.html', event=event, form=form)


@app.route('/events/feedback/<event_id>', methods=['GET', 'POST'])
def submit_feedback(event_id):
    """
    This function submit the feedback for an event  only when feedback is not given
    """
    event = Event.query.get(event_id)
    form = EventFeedbackForm()
    if form.validate_on_submit():

        # Check if the user has already provided feedback for the event
        existing_feedback = Feedback.query.filter_by(event_id=event.id, user_id=current_user.id).first()
        if existing_feedback:
            flash('You have already submitted feedback for this event.')
            return render_template('feedback_form.html', form=form, event=event, error_message=True)

        # Save the rating and comment to the database
        try:
            feedback = Feedback(
                event_id=event.id,
                user_id=current_user.id,
                rating=form.rating.data,
                comment=form.comment.data
            )
            db.session.add(feedback)
            db.session.commit()
            message = "Feedback is  Submitted"
            flash('Feedback submitted successfully!')
            return redirect(url_for('user_participated_events', message=message))
        except Exception as e:
            flash(f"error occurred when submitting the feedback data to DB {e}")
    return render_template('feedback_form.html', form=form, event=event)


@app.route('/event_details/<event_id>/event-feedbacks')
def get_event_feedbacks(event_id):
    """
    This function will get the all feedbacks from the participant for an event
    """
    try:
        event = Event.query.get(event_id)
        event_feedbacks = Feedback.query.filter_by(event_id=event.id).all()
        return render_template('event_feedbacks.html', event=event, event_feedbacks=event_feedbacks)
    except Exception as e:
        flash(f"error occurred when getting the feedback details{e}")


@app.route('/dashboard')
def dashboard():
    """
    This function will render the html template to display the graphs
    """
    generate_graph()
    return render_template('analytics_dashboard.html')
