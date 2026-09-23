from datetime import datetime, date
from . import db

class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    workout_type = db.Column(db.String(50), nullable=False)  # e.g., Running, Strength Training, Cycling, Yoga, Cardio, Swimming, Walking, HIIT
    exercise_name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    sets = db.Column(db.Integer, nullable=True, default=0)
    repetitions = db.Column(db.Integer, nullable=True, default=0)
    calories_burned = db.Column(db.Float, nullable=False, default=0.0)
    workout_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, user_id=None, workout_type=None, exercise_name=None, duration=None, sets=0, repetitions=0, calories_burned=0.0, workout_date=None, notes=None, **kwargs):
        self.user_id = user_id
        self.workout_type = workout_type
        self.exercise_name = exercise_name
        self.duration = duration
        self.sets = sets
        self.repetitions = repetitions
        self.calories_burned = calories_burned
        self.workout_date = workout_date
        self.notes = notes
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def icon(self):
        """Return a suitable Bootstrap icon name for workout type."""
        icons = {
            'Running': 'bi-person-walking',
            'Walking': 'bi-person-walking',
            'Cycling': 'bi-bicycle',
            'Strength Training': 'bi-lightning-charge-fill',
            'Yoga': 'bi-flower1',
            'Cardio': 'bi-heart-pulse-fill',
            'Swimming': 'bi-water',
            'HIIT': 'bi-fire',
            'Pilates': 'bi-activity'
        }
        return icons.get(self.workout_type, 'bi-activity')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'workout_type': self.workout_type,
            'exercise_name': self.exercise_name,
            'duration': self.duration,
            'sets': self.sets,
            'repetitions': self.repetitions,
            'calories_burned': self.calories_burned,
            'workout_date': self.workout_date.strftime('%Y-%m-%d'),
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<Workout {self.exercise_name} ({self.workout_type}) on {self.workout_date}>'
