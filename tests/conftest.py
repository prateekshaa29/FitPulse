import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, User, Workout, Goal, WeightRecord

@pytest.fixture
def app():
    """Create and configure a clean testing application."""
    test_app = create_app('testing')

    with test_app.app_context():
        db.create_all()
        
        # Create standard test accounts
        user = User(
            name='Test Athlete',
            email='athlete@test.com',
            role='user',
            age=25,
            gender='Male',
            height=180.0,
            weight=75.0
        )
        user.set_password('Secret123')
        db.session.add(user)

        other_user = User(
            name='Other Athlete',
            email='other@test.com',
            role='user',
            age=30,
            gender='Female',
            height=165.0,
            weight=60.0
        )
        other_user.set_password('Secret123')
        db.session.add(other_user)

        trainer = User(
            name='Test Trainer',
            email='trainer@test.com',
            role='trainer',
            age=35,
            gender='Male',
            height=185.0,
            weight=85.0
        )
        trainer.set_password('Secret123')
        db.session.add(trainer)

        nutritionist = User(
            name='Test Nutritionist',
            email='nutritionist@test.com',
            role='nutritionist',
            age=32,
            gender='Female',
            height=170.0,
            weight=62.0
        )
        nutritionist.set_password('Secret123')
        db.session.add(nutritionist)

        admin = User(
            name='Test Admin',
            email='admin@test.com',
            role='admin',
            age=40,
            gender='Other',
            height=175.0,
            weight=70.0
        )
        admin.set_password('Secret123')
        db.session.add(admin)

        db.session.commit()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, email='athlete@test.com', password='Secret123'):
        return self._client.post(
            '/login',
            data={'email': email, 'password': password},
            follow_redirects=True
        )

    def logout(self):
        return self._client.get('/logout', follow_redirects=True)


@pytest.fixture
def auth(client):
    return AuthActions(client)
