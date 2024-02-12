from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError

from .model import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('username', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('confirm_password', message='Password must match!')])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register!')


class EventOrganizerForm(FlaskForm):
    try:
        name = StringField('Event Name', validators=[DataRequired()])
        description = TextAreaField('Description', validators=[DataRequired()])
        datetime = DateTimeField('Date and Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()],
                                 description='Format: YYYY-MM-DD HH:MM')
        location = StringField('Location')
        submit = SubmitField('Organize Event')
    except Exception as e:
        print(f"An error occurred when creating event organizer form {e}")


class UpdateEventForm(FlaskForm):
    try:
        name = StringField('Name', validators=[DataRequired()])
        description = TextAreaField('Description', validators=[DataRequired()])
        datetime = DateTimeField('Date and Time', validators=[DataRequired()])
        location = StringField('Location')
    except Exception as e:
        print(f"An error occurred when creating event organizer form {e}")
