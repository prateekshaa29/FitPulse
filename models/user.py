from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'user', 'trainer', 'nutritionist', 'admin'
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)  # 'Male', 'Female', 'Other', 'Prefer not to say'
    height = db.Column(db.Float, nullable=True)  # in cm
    weight = db.Column(db.Float, nullable=True)  # in kg
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    workouts = db.relationship('Workout', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', lazy=True, cascade='all, delete-orphan')
    weight_records = db.relationship('WeightRecord', backref='user', lazy=True, cascade='all, delete-orphan', order_by='WeightRecord.date.desc()')
    recommendations_received = db.relationship(
        'Recommendation',
        foreign_keys='Recommendation.user_id',
        backref='client',
        lazy=True,
        cascade='all, delete-orphan'
    )
    recommendations_given = db.relationship(
        'Recommendation',
        foreign_keys='Recommendation.author_id',
        backref='author',
        lazy=True
    )

    def __init__(self, name=None, email=None, role='user', age=None, gender=None, height=None, weight=None, password_hash=None, **kwargs):
        self.name = name
        self.email = email
        self.role = role
        self.age = age
        self.gender = gender
        self.height = height
        self.weight = weight
        if password_hash:
            self.password_hash = password_hash
        for k, v in kwargs.items():
            setattr(self, k, v)

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the user's password."""
        return check_password_hash(self.password_hash, password)

    @property
    def bmi(self):
        """Calculate BMI = weight (kg) / (height (m))^2."""
        if self.height and self.weight and self.height > 0 and self.weight > 0:
            height_in_meters = self.height / 100.0
            return round(self.weight / (height_in_meters ** 2), 1)
        return None

    @property
    def bmi_category(self):
        """Determine BMI standard WHO category."""
        bmi_val = self.bmi
        if bmi_val is None:
            return 'Not Recorded'
        if bmi_val < 18.5:
            return 'Underweight'
        elif 18.5 <= bmi_val < 25.0:
            return 'Normal weight'
        elif 25.0 <= bmi_val < 30.0:
            return 'Overweight'
        else:
            return 'Obesity'

    @property
    def bmi_badge_color(self):
        """Bootstrap color indicator for BMI category."""
        cat = self.bmi_category
        if cat == 'Normal weight':
            return 'success'
        elif cat == 'Underweight':
            return 'info'
        elif cat == 'Overweight':
            return 'warning'
        elif cat == 'Obesity':
            return 'danger'
        return 'secondary'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'age': self.age,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'bmi': self.bmi,
            'bmi_category': self.bmi_category,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
