from datetime import date, timedelta
from models import db, Goal, User

def test_add_goal(client, auth, app):
    """Test adding a new fitness goal."""
    auth.login('athlete@test.com', 'Secret123')

    target_date = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
    response = client.post('/goals/add', data={
        'goal_type': 'Lose Weight',
        'target_value': '70 kg',
        'current_value': '75 kg',
        'start_date': date.today().strftime('%Y-%m-%d'),
        'target_date': target_date,
        'description': 'Targeting 5 kg reduction.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Lose Weight' in response.data

    with app.app_context():
        user = User.query.filter_by(email='athlete@test.com').first()
        goal = Goal.query.filter_by(user_id=user.id, goal_type='Lose Weight').first()
        assert goal is not None
        assert goal.target_value == '70 kg'
        assert goal.status == 'ACTIVE'


def test_toggle_goal_status(client, auth, app):
    """Test toggling goal status to COMPLETED."""
    auth.login('athlete@test.com', 'Secret123')

    with app.app_context():
        user = User.query.filter_by(email='athlete@test.com').first()
        g = Goal(
            user_id=user.id,
            goal_type='Run Distance',
            target_value='10 km',
            start_date=date.today(),
            target_date=date.today() + timedelta(days=15),
            status='ACTIVE'
        )
        db.session.add(g)
        db.session.commit()
        g_id = g.id

    response = client.post(f'/goals/{g_id}/status', follow_redirects=True)
    assert response.status_code == 200
    assert b'marked as Completed' in response.data

    with app.app_context():
        updated = db.session.get(Goal, g_id)
        assert updated.status == 'COMPLETED'


def test_delete_goal(client, auth, app):
    """Test deleting a goal."""
    auth.login('athlete@test.com', 'Secret123')

    with app.app_context():
        user = User.query.filter_by(email='athlete@test.com').first()
        g = Goal(
            user_id=user.id,
            goal_type='Workout Frequency',
            target_value='20 Workouts',
            start_date=date.today(),
            target_date=date.today() + timedelta(days=30)
        )
        db.session.add(g)
        db.session.commit()
        g_id = g.id

    response = client.post(f'/goals/{g_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Goal deleted successfully' in response.data

    with app.app_context():
        assert db.session.get(Goal, g_id) is None
