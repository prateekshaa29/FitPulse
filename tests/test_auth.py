from models import User

def test_register_success(client, app):
    """Test successful user registration."""
    response = client.post('/register', data={
        'name': 'New Runner',
        'email': 'runner@test.com',
        'password': 'RunnerPass123',
        'confirm_password': 'RunnerPass123',
        'gender': 'Female',
        'age': '24',
        'height': '168.0',
        'weight': '58.5'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Account registered successfully' in response.data

    with app.app_context():
        user = User.query.filter_by(email='runner@test.com').first()
        assert user is not None
        assert user.name == 'New Runner'
        assert user.role == 'user'
        assert user.check_password('RunnerPass123') is True
        assert user.weight == 58.5


def test_register_trainer_and_nutritionist(client, app):
    """Test registering as a trainer and nutritionist."""
    # Register Trainer
    res_trainer = client.post('/register', data={
        'name': 'Coach Mike',
        'email': 'mike@trainer.com',
        'role': 'trainer',
        'password': 'CoachPassword123',
        'confirm_password': 'CoachPassword123'
    }, follow_redirects=True)
    assert res_trainer.status_code == 200
    assert b'Account registered successfully' in res_trainer.data

    # Register Nutritionist
    res_nutri = client.post('/register', data={
        'name': 'Dr. Anna Nutri',
        'email': 'anna@nutrition.com',
        'role': 'nutritionist',
        'password': 'NutriPassword123',
        'confirm_password': 'NutriPassword123'
    }, follow_redirects=True)
    assert res_nutri.status_code == 200
    assert b'Account registered successfully' in res_nutri.data

    with app.app_context():
        trainer = User.query.filter_by(email='mike@trainer.com').first()
        nutritionist = User.query.filter_by(email='anna@nutrition.com').first()
        assert trainer is not None and trainer.role == 'trainer'
        assert nutritionist is not None and nutritionist.role == 'nutritionist'


def test_register_duplicate_email(client):
    """Test duplicate email rejection."""
    response = client.post('/register', data={
        'name': 'Duplicate User',
        'email': 'athlete@test.com',  # existing in conftest
        'password': 'Password123',
        'confirm_password': 'Password123'
    }, follow_redirects=True)

    assert b'An account with this email address already exists' in response.data


def test_register_password_mismatch(client):
    """Test password and confirm password mismatch."""
    response = client.post('/register', data={
        'name': 'Mismatch User',
        'email': 'mismatch@test.com',
        'password': 'Password123',
        'confirm_password': 'DifferentPassword456'
    }, follow_redirects=True)

    assert b'Passwords do not match' in response.data


def test_login_success(auth):
    """Test valid login authentication."""
    response = auth.login('athlete@test.com', 'Secret123')
    assert response.status_code == 200
    assert b'Welcome back, Test Athlete' in response.data


def test_login_invalid_password(auth):
    """Test invalid password rejection."""
    response = auth.login('athlete@test.com', 'WrongPassword')
    assert response.status_code == 200
    assert b'Invalid email address or password' in response.data


def test_logout(auth):
    """Test logout destroys session."""
    auth.login('athlete@test.com', 'Secret123')
    response = auth.logout()
    assert response.status_code == 200
    assert b'You have been logged out successfully' in response.data
