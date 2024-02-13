from .auth.forms import LoginForm, EventFeedbackForm, EventOrganizerForm
from .auth.model import User
from .auth import app

app.config['WTF_CSRF_ENABLED'] = False


def test_login_form_valid():
    with app.app_context():
        form = LoginForm(email='user5@abc.com', password='1234')
        assert form.validate() == True


def test_login_form_missing_pass():
    with app.app_context():
        form = LoginForm(email='user5@abc.com', password='')
        assert form.validate() == False


def test_feedback_form_valid_rating():
    with app.app_context():
        form = EventFeedbackForm(rating=5, comment='Great event!')
        assert form.validate() == True


def test_feedback_form_invalid_rating():
    with app.app_context():
        form = EventFeedbackForm(rating=6, comment='Great event!')
        assert form.validate() == False


def test_user_model_valid_details():
    with app.app_context():
        user = User(email='test1@gmail.com',password= '1234',username="test1", phone_number="1234567890")
        assert user.email == 'test1@gmail.com'
        assert user.hashed_password != '12345'


