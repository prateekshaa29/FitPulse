import re
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, WeightRecord
from . import get_role_dashboard

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user account."""
    if 'user_id' in session:
        return redirect(url_for(get_role_dashboard(session.get('user_role'))))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'user').strip()
        gender = request.form.get('gender', '').strip()
        age = request.form.get('age', '').strip()
        height = request.form.get('height', '').strip()
        weight = request.form.get('weight', '').strip()

        # Sanitize role (prevent registering directly as admin for security)
        if role not in ['user', 'trainer', 'nutritionist']:
            role = 'user'

        errors = []

        # Validations
        if not name or len(name) < 2:
            errors.append('Please provide a valid full name (minimum 2 characters).')

        if not email or not re.match(EMAIL_REGEX, email):
            errors.append('Please provide a valid email address.')
        elif User.query.filter_by(email=email).first():
            errors.append('An account with this email address already exists.')

        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        elif password != confirm_password:
            errors.append('Passwords do not match.')

        # Numerical validations
        parsed_age = None
        if age:
            try:
                parsed_age = int(age)
                if parsed_age < 5 or parsed_age > 120:
                    errors.append('Age must be between 5 and 120 years.')
            except ValueError:
                errors.append('Age must be a valid integer.')

        parsed_height = None
        if height:
            try:
                parsed_height = float(height)
                if parsed_height < 50 or parsed_height > 260:
                    errors.append('Height must be between 50 cm and 260 cm.')
            except ValueError:
                errors.append('Height must be a valid number.')

        parsed_weight = None
        if weight:
            try:
                parsed_weight = float(weight)
                if parsed_weight < 20 or parsed_weight > 400:
                    errors.append('Weight must be between 20 kg and 400 kg.')
            except ValueError:
                errors.append('Weight must be a valid number.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'register.html',
                name=name,
                email=email,
                role=role,
                gender=gender,
                age=age,
                height=height,
                weight=weight
            )

        # Create user
        new_user = User(
            name=name,
            email=email,
            role=role,
            gender=gender if gender else None,
            age=parsed_age,
            height=parsed_height,
            weight=parsed_weight
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()  # to obtain new_user.id

        # If weight provided, log initial weight record
        if parsed_weight:
            initial_weight_log = WeightRecord(
                user_id=new_user.id,
                weight=parsed_weight,
                date=date.today(),
                notes='Initial weight during registration'
            )
            db.session.add(initial_weight_log)

        db.session.commit()
        flash('Account registered successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate user and initialize session."""
    if 'user_id' in session:
        return redirect(url_for(get_role_dashboard(session.get('user_role'))))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please provide both email and password.', 'warning')
            return render_template('login.html', email=email)

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email address or password.', 'danger')
            return render_template('login.html', email=email)

        # Establish session
        session.clear()
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['user_role'] = user.role

        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(url_for(get_role_dashboard(user.role)))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Destroy user session and log out."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
