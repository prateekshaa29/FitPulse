from datetime import date
from models import User
from routes.bmi import calculate_bmi_details

def test_add_weight_and_user_sync(client, auth, app):
    """Test logging weight and ensuring user current weight syncs."""
    auth.login('athlete@test.com', 'Secret123')

    response = client.post('/weight/add', data={
        'weight': '73.2',
        'date': date.today().strftime('%Y-%m-%d'),
        'notes': 'Post morning run'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'73.2 kg logged successfully' in response.data

    with app.app_context():
        user = User.query.filter_by(email='athlete@test.com').first()
        assert user.weight == 73.2
        # BMI for 73.2 kg & 180 cm => 73.2 / (1.8^2) = 22.59 => 22.6
        assert user.bmi == 22.6
        assert user.bmi_category == 'Normal weight'


def test_bmi_math_and_categories():
    """Test WHO standard BMI categories and mathematical precision."""
    # Underweight (< 18.5)
    underweight = calculate_bmi_details(50.0, 180.0)
    assert underweight['bmi'] == 15.4
    assert underweight['category'] == 'Underweight'

    # Normal weight (18.5 - 24.9)
    normal = calculate_bmi_details(70.0, 175.0)
    assert normal['bmi'] == 22.9
    assert normal['category'] == 'Normal weight'

    # Overweight (25.0 - 29.9)
    overweight = calculate_bmi_details(85.0, 175.0)
    assert overweight['bmi'] == 27.8
    assert overweight['category'] == 'Overweight'

    # Obesity (>= 30.0)
    obese = calculate_bmi_details(105.0, 175.0)
    assert obese['bmi'] == 34.3
    assert obese['category'] == 'Obesity'


def test_bmi_api_endpoint(client):
    """Test the JSON API calculation endpoint."""
    response = client.post('/api/bmi/calculate', json={
        'height': 170.0,
        'weight': 68.0
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['bmi'] == 23.5
    assert data['category'] == 'Normal weight'
    assert 'min_healthy_weight' in data
