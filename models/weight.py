from datetime import datetime, date
from . import db

class WeightRecord(db.Model):
    __tablename__ = 'weight_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    weight = db.Column(db.Float, nullable=False)  # in kg
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, user_id=None, weight=None, date=None, notes=None, **kwargs):
        self.user_id = user_id
        self.weight = weight
        self.date = date
        self.notes = notes
        for k, v in kwargs.items():
            setattr(self, k, v)

    def bmi_for_height(self, height_cm):
        """Calculate BMI given height in cm for this weight record."""
        if height_cm and height_cm > 0 and self.weight > 0:
            height_m = height_cm / 100.0
            return round(self.weight / (height_m ** 2), 1)
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'weight': self.weight,
            'date': self.date.strftime('%Y-%m-%d'),
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<WeightRecord {self.weight} kg on {self.date} for user {self.user_id}>'
