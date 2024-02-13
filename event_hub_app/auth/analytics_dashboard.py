from .model import User, Event, Feedback
import pandas as pd


def get_event_data():
    events = Event.query.all()

    event_names = []
    event_ratings = []
    event_participants = []

    event_dataframe = None
    for event in events:
        event_names.append(event.name)

        ratings = [feedback.rating for feedback in event.feedback]
        if ratings:
            average_rating = sum(ratings) / len(ratings)
        else:
            average_rating = 0
        event_ratings.append(average_rating)

        participation_count = len(event.participants)
        event_participants.append(participation_count)

        # Create DataFrame
        print("Events:", event_names)
        print("Rating:", event_ratings)
        print("parti:",event_participants)
        event_dataframe = pd.DataFrame({
            'Events': event_names,
            'Rating': event_ratings,
            'Participation': event_participants
        })
    return event_dataframe
