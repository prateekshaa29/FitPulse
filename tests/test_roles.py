from models import db, User, Recommendation

def test_user_forbidden_access(client, auth):
    """Test standard user is blocked from accessing specialized portals."""
    auth.login('athlete@test.com', 'Secret123')

    # Attempt Admin Dashboard
    res_admin = client.get('/admin/dashboard', follow_redirects=True)
    assert b'You do not have permission to access this resource' in res_admin.data

    # Attempt Trainer Dashboard
    res_trainer = client.get('/trainer/dashboard', follow_redirects=True)
    assert b'You do not have permission to access this resource' in res_trainer.data

    # Attempt Nutritionist Dashboard
    res_nutr = client.get('/nutritionist/dashboard', follow_redirects=True)
    assert b'You do not have permission to access this resource' in res_nutr.data


def test_trainer_portal_and_recommendation(client, auth, app):
    """Test trainer can view dashboard and prescribe workout guidance."""
    auth.login('trainer@test.com', 'Secret123')

    res = client.get('/trainer/dashboard')
    assert res.status_code == 200
    assert b'Trainer Portal' in res.data

    with app.app_context():
        athlete = User.query.filter_by(email='athlete@test.com').first()
        athlete_id = athlete.id

    # Prescribe workout recommendation
    post_res = client.post(f'/trainer/users/{athlete_id}/recommend', data={
        'title': 'Form Check: Squats',
        'content': 'Keep your chest elevated and push through mid-foot.'
    }, follow_redirects=True)

    assert post_res.status_code == 200
    assert b'Workout recommendation provided' in post_res.data

    with app.app_context():
        rec = Recommendation.query.filter_by(user_id=athlete_id, note_type='WORKOUT').first()
        assert rec is not None
        assert rec.title == 'Form Check: Squats'


def test_nutritionist_portal_and_recommendation(client, auth, app):
    """Test nutritionist can view dashboard and prescribe dietary guidance."""
    auth.login('nutritionist@test.com', 'Secret123')

    res = client.get('/nutritionist/dashboard')
    assert res.status_code == 200
    assert b'Nutritionist Portal' in res.data

    with app.app_context():
        athlete = User.query.filter_by(email='athlete@test.com').first()
        athlete_id = athlete.id

    # Prescribe dietary recommendation
    post_res = client.post(f'/nutritionist/users/{athlete_id}/recommend', data={
        'title': 'Electrolyte Strategy',
        'content': 'Add 500mg sodium in 750ml water prior to tempo runs.'
    }, follow_redirects=True)

    assert post_res.status_code == 200
    assert b'Nutrition guidance sent' in post_res.data

    with app.app_context():
        rec = Recommendation.query.filter_by(user_id=athlete_id, note_type='NUTRITION').first()
        assert rec is not None
        assert rec.title == 'Electrolyte Strategy'


def test_admin_full_management(client, auth, app):
    """Test admin can view dashboard, create, edit, and delete users."""
    auth.login('admin@test.com', 'Secret123')

    res = client.get('/admin/dashboard')
    assert res.status_code == 200
    assert b'System Administration' in res.data

    # Admin create new user
    res_create = client.post('/admin/users/create', data={
        'name': 'Admin Created User',
        'email': 'admincreated@test.com',
        'password': 'Password123',
        'role': 'trainer'
    }, follow_redirects=True)

    assert res_create.status_code == 200
    assert b'Admin Created User' in res_create.data

    with app.app_context():
        u = User.query.filter_by(email='admincreated@test.com').first()
        assert u is not None
        assert u.role == 'trainer'
        u_id = u.id

    # Admin delete created user
    res_delete = client.post(f'/admin/users/{u_id}/delete', follow_redirects=True)
    assert res_delete.status_code == 200
    assert b'deleted successfully' in res_delete.data

    with app.app_context():
        assert db.session.get(User, u_id) is None
