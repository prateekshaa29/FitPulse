from flask import Blueprint, render_template, request, jsonify
from models import WeightRecord
from . import get_current_user

bmi_bp = Blueprint('bmi', __name__)

def calculate_bmi_details(weight_kg, height_cm):
    """Compute BMI, category, healthy weight range, and color."""
    if not weight_kg or not height_cm or weight_kg <= 0 or height_cm <= 0:
        return None

    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m ** 2), 1)

    # Standard WHO categories
    if bmi < 18.5:
        category = 'Underweight'
        color = 'info'
        advice = 'You are below the normal weight range. Consider consulting a nutritionist for healthy weight-gain nutrition strategies.'
    elif 18.5 <= bmi < 25.0:
        category = 'Normal weight'
        color = 'success'
        advice = 'Congratulations! Your BMI is within the healthy range. Maintain your active lifestyle and balanced diet.'
    elif 25.0 <= bmi < 30.0:
        category = 'Overweight'
        color = 'warning'
        advice = 'You are slightly above the standard healthy range. Regular cardio and strength workouts alongside calorie awareness can help achieve optimal balance.'
    else:
        category = 'Obesity'
        color = 'danger'
        advice = 'Your BMI is in the obesity category. It is recommended to consult a healthcare provider or nutritionist to design a safe, gradual fitness and meal plan.'

    # Healthy weight range (BMI 18.5 to 24.9)
    min_healthy_weight = round(18.5 * (height_m ** 2), 1)
    max_healthy_weight = round(24.9 * (height_m ** 2), 1)

    return {
        'bmi': bmi,
        'category': category,
        'color': color,
        'advice': advice,
        'height_cm': height_cm,
        'weight_kg': weight_kg,
        'min_healthy_weight': min_healthy_weight,
        'max_healthy_weight': max_healthy_weight
    }

@bmi_bp.route('/bmi')
def view_calculator():
    """Render BMI calculator page with user's saved data if available."""
    user = get_current_user()
    initial_height = user.height if user and user.height else 170.0
    initial_weight = user.weight if user and user.weight else 70.0

    bmi_details = calculate_bmi_details(initial_weight, initial_height)

    # User's recent BMI history
    bmi_history = []
    if user and user.height:
        records = WeightRecord.query.filter_by(user_id=user.id).order_by(WeightRecord.date.desc()).limit(8).all()
        for r in records:
            bmi_history.append({
                'date': r.date.strftime('%Y-%m-%d'),
                'weight': r.weight,
                'bmi': r.bmi_for_height(user.height)
            })

    return render_template(
        'bmi.html',
        user=user,
        initial_height=initial_height,
        initial_weight=initial_weight,
        bmi_details=bmi_details,
        bmi_history=bmi_history
    )


@bmi_bp.route('/api/bmi/calculate', methods=['POST'])
def api_calculate():
    """JSON API endpoint for BMI calculation."""
    data = request.get_json() or {}
    try:
        height = float(data.get('height', 0))
        weight = float(data.get('weight', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid numeric values'}), 400

    details = calculate_bmi_details(weight, height)
    if not details:
        return jsonify({'error': 'Height and weight must be positive numbers'}), 400

    return jsonify(details)
