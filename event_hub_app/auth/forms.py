from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange


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
        date_time = DateTimeField('Date and Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()],
                                  description='Format: YYYY-MM-DD HH:MM')
        duration = StringField('Duration in Minutes')
        location = StringField('Location')
        submit = SubmitField('Organize Event')
    except Exception as e:
        print(f"An error occurred when creating event organizer form {e}")


class UpdateEventForm(FlaskForm):
    try:
        name = StringField('Name', validators=[DataRequired()])
        description = TextAreaField('Description', validators=[DataRequired()])
        date_time = DateTimeField('Date and Time', validators=[DataRequired()])
        duration = StringField('Name', validators=[DataRequired()])
        location = StringField('Location')
    except Exception as e:
        print(f"An error occurred when creating event organizer form {e}")


class EventFeedbackForm(FlaskForm):
    try:
        rating = IntegerField('Rating', validators=[DataRequired(),
                                                    NumberRange(min=1, max=5,
                                                                message="Rating must be between 1 and 5")])
        comment = TextAreaField('comments')
        submit = SubmitField('Submit Feedback')
    except Exception as e:
        print(f"An error occurred when creating event feedback form {e}")
