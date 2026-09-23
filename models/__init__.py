from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .workout import Workout
from .goal import Goal
from .weight import WeightRecord
from .recommendation import Recommendation

__all__ = ['db', 'User', 'Workout', 'Goal', 'WeightRecord', 'Recommendation']
