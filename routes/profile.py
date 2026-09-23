from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, WeightRecord
from . import login_required, get_current_user

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    """View and update profile information."""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        gender = request.form.get('gender', '').strip()
        height = request.form.get('height', '').strip()
        weight = request.form.get('weight', '').strip()

        errors = []
        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters long.')

        parsed_age = None
        if age:
            try:
                parsed_age = int(age)
                if parsed_age < 5 or parsed_age > 120:
                    errors.append('Age must be between 5 and 120.')
            except ValueError:
                errors.append('Invalid age value.')

        parsed_height = None
        if height:
            try:
                parsed_height = float(height)
                if parsed_height < 50 or parsed_height > 260:
                    errors.append('Height must be between 50 cm and 260 cm.')
            except ValueError:
                errors.append('Invalid height value.')

        parsed_weight = None
        if weight:
            try:
                parsed_weight = float(weight)
                if parsed_weight < 20 or parsed_weight > 400:
                    errors.append('Weight must be between 20 kg and 400 kg.')
            except ValueError:
                errors.append('Invalid weight value.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('profile.html', user=user)

        user.name = name
        user.age = parsed_age
        user.gender = gender if gender else None
        user.height = parsed_height

        # If weight updated, also log a weight history entry
        if parsed_weight is not None and parsed_weight != user.weight:
            user.weight = parsed_weight
            weight_entry = WeightRecord(
                user_id=user.id,
                weight=parsed_weight,
                date=date.today(),
                notes='Profile update'
            )
            db.session.add(weight_entry)

        db.session.commit()
        session['user_name'] = user.name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.view_profile'))

    return render_template('profile.html', user=user)
