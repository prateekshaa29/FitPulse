from datetime import date
from models import db, Workout, User

def test_add_workout(client, auth, app):
    """Test adding a new workout."""
    auth.login('athlete@test.com', 'Secret123')

    response = client.post('/workouts/add', data={
        'workout_type': 'Running',
        'exercise_name': 'Evening 5K',
        'duration': '30',
        'sets': '1',
        'repetitions': '5',
        'calories_burned': '320.0',
        'workout_date': '2026-03-15',
        'notes': 'Great cadence and breathing.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Evening 5K' in response.data

    with app.app_context():
        user = User.query.filter_by(email='athlete@test.com').first()
        workout = Workout.query.filter_by(user_id=user.id, exercise_name='Evening 5K').first()
        assert workout is not None
        assert workout.duration == 30
        assert workout.calories_burned == 320.0
        assert workout.workout_type == 'Running'


def test_edit_workout(client, auth, app):
    """Test editing an existing workout."""
    auth.login('athlete@test.com', 'Secret123')

    # Add initial workout
    with app.app_context():
        user = User.query.filter_by(email='athlete@test.com').first()
        w = Workout(
            user_id=user.id,
            workout_type='Strength Training',
            exercise_name='Bench Press',
            duration=45,
            sets=4,
            repetitions=10,
            calories_burned=280.0,
            workout_date=date(2026, 3, 10)
        )
        db.session.add(w)
        db.session.commit()
        w_id = w.id

    # Edit workout
    response = client.post(f'/workouts/{w_id}/edit', data={
        'workout_type': 'Strength Training',
        'exercise_name': 'Heavy Bench Press',
        'duration': '50',
        'sets': '5',
        'repetitions': '5',
        'calories_burned': '310.0',
        'workout_date': '2026-03-10',
        'notes': 'New personal best!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Heavy Bench Press' in response.data

    with app.app_context():
        updated = db.session.get(Workout, w_id)
        assert updated.exercise_name == 'Heavy Bench Press'
        assert updated.duration == 50


def test_delete_workout(client, auth, app):
    """Test deleting a workout."""
    auth.login('athlete@test.com', 'Secret123')

    with app.app_context():
        user = User.query.filter_by(email='athlete@test.com').first()
        w = Workout(
            user_id=user.id,
            workout_type='Yoga',
            exercise_name='Morning Flow',
            duration=30,
            calories_burned=120.0,
            workout_date=date.today()
        )
        db.session.add(w)
        db.session.commit()
        w_id = w.id

    response = client.post(f'/workouts/{w_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Workout record deleted successfully' in response.data

    with app.app_context():
        deleted = db.session.get(Workout, w_id)
        assert deleted is None


def test_workout_isolation(client, auth, app):
    """Test user cannot delete or edit other user's workout."""
    with app.app_context():
        other_user = User.query.filter_by(email='other@test.com').first()
        w = Workout(
            user_id=other_user.id,
            workout_type='Cycling',
            exercise_name='Private Ride',
            duration=60,
            calories_burned=400.0,
            workout_date=date.today()
        )
        db.session.add(w)
        db.session.commit()
        other_workout_id = w.id

    # Log in as different user
    auth.login('athlete@test.com', 'Secret123')

    # Attempt to delete other user's workout
    response = client.post(f'/workouts/{other_workout_id}/delete', follow_redirects=True)
    assert b'You are not authorized to delete this workout' in response.data

    with app.app_context():
        # Ensure it still exists
        assert db.session.get(Workout, other_workout_id) is not None
