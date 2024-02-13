from datetime import datetime
from flask_login import UserMixin
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except Exception as e:
        print(f"An error occurred while loading the user: {e}")
        return None


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)

    organized_events = db.relationship('Event', backref='organizer', lazy=True)

    def __init__(self, username, password, email, phone_number):
        self.username = username
        self.hashed_password = generate_password_hash(password)
        self.email = email
        self.phone_number = phone_number

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    duration = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(100))
    organizer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    feedback = db.relationship('Feedback', backref='event', lazy=True)
    participants = db.relationship('User', secondary='event_participant', backref='attended_events')

    def __init__(self, name, description, date_time, event_duration, location, organizer_id):
        self.name = name
        self.description = description
        self.date_time = date_time
        self.duration = event_duration
        self.location = location
        self.organizer_id = organizer_id

    def check_event_name(self, event_name):
        return self.name != event_name


class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(36), db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text)
    rating = db.Column(db.Integer)

    def __init__(self, event_id, user_id, rating, comment):
        self.event_id = event_id
        self.user_id = user_id
        self.rating = rating
        self.comment = comment


event_participant = db.Table(
    'event_participant',
    db.Column('event_id', db.String(36), db.ForeignKey('events.id'), primary_key=True),
    db.Column('participant_id', db.String(36), db.ForeignKey('users.id'), primary_key=True)
)
