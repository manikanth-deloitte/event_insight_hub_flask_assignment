from .model import User, Event, Feedback
import pandas as pd
import matplotlib.pyplot as plt
import os


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


def generate_graph():
    event_dataframe = get_event_data()
    top_events_by_rating = event_dataframe.sort_values(by='Rating', ascending=False).head(3)
    top_events_by_participation = event_dataframe.sort_values(by='Participation', ascending=False).head(3)

    # Plotting
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 10))

    # Top events by rating
    axes[0].bar(top_events_by_rating['Events'], top_events_by_rating['Rating'], color='blue')
    axes[0].set_title('Top 3 Events Based on Rating')
    axes[0].set_ylabel('Rating')

    # Top events by participation
    axes[1].bar(top_events_by_participation['Events'], top_events_by_participation['Participation'], color='green')
    axes[1].set_title('Top 3 Events Based on Participation')
    axes[1].set_ylabel('Participation')

    # Adjust layout
    plt.tight_layout()

    current_directory = os.getcwd()
    path = os.path.join(current_directory, 'auth', 'static')
    file_name = os.path.join(path, 'Top_event_graph.png')
    plt.savefig(file_name)
