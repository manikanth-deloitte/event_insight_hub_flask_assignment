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

    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)

    # organized_events = db.relationship('Event', backref='organizer', lazy=True)

    def __init__(self, username, password, email, phone_number):
        self.username = username
        self.hashed_password = generate_password_hash(password)
        self.email = email
        self.phone_number = phone_number

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
