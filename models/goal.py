from datetime import datetime, date
from . import db

class Goal(db.Model):
    __tablename__ = 'goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    goal_type = db.Column(db.String(50), nullable=False)  # Lose Weight, Gain Weight, Run Distance, Workout Frequency, Improve Strength, Burn Calories
    target_value = db.Column(db.String(100), nullable=False)  # e.g., '70 kg', '10 km', '5 workouts/week'
    current_value = db.Column(db.String(100), nullable=True)  # e.g., '75 kg', '6 km', '3 workouts'
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    target_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='ACTIVE')  # 'ACTIVE', 'COMPLETED', 'EXPIRED'
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, user_id=None, goal_type=None, target_value=None, current_value=None, start_date=None, target_date=None, status='ACTIVE', description=None, **kwargs):
        self.user_id = user_id
        self.goal_type = goal_type
        self.target_value = target_value
        self.current_value = current_value
        self.start_date = start_date
        self.target_date = target_date
        self.status = status
        self.description = description
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def is_expired(self):
        """Check if active goal passed target date."""
        if self.status == 'ACTIVE' and self.target_date < date.today():
            return True
        return False

    @property
    def badge_color(self):
        if self.status == 'COMPLETED':
            return 'success'
        elif self.is_expired:
            return 'danger'
        return 'primary'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'goal_type': self.goal_type,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'target_date': self.target_date.strftime('%Y-%m-%d'),
            'status': self.status,
            'is_expired': self.is_expired,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<Goal {self.goal_type} ({self.status}) for user {self.user_id}>'
