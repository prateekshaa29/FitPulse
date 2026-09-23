import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User, Workout, Goal, WeightRecord, Recommendation
from . import login_required, role_required, get_current_user

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    """Admin dashboard overview."""
    admin = get_current_user()

    total_users = User.query.count()
    users_by_role = {
        'user': User.query.filter_by(role='user').count(),
        'trainer': User.query.filter_by(role='trainer').count(),
        'nutritionist': User.query.filter_by(role='nutritionist').count(),
        'admin': User.query.filter_by(role='admin').count()
    }

    total_workouts = Workout.query.count()
    total_goals = Goal.query.count()
    total_weights = WeightRecord.query.count()
    total_recommendations = Recommendation.query.count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(6).all()
    recent_workouts = Workout.query.order_by(Workout.created_at.desc()).limit(6).all()

    return render_template(
        'admin/dashboard.html',
        admin=admin,
        total_users=total_users,
        users_by_role=users_by_role,
        total_workouts=total_workouts,
        total_goals=total_goals,
        total_weights=total_weights,
        total_recommendations=total_recommendations,
        recent_users=recent_users,
        recent_workouts=recent_workouts
    )


@admin_bp.route('/users')
@login_required
@role_required('admin')
def list_users():
    """Manage all users."""
    role_filter = request.args.get('role', '').strip()
    search = request.args.get('search', '').strip()

    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    if search:
        query = query.filter(
            (User.name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )

    users = query.order_by(User.id.asc()).all()
    return render_template('admin/users.html', users=users, role_filter=role_filter, search=search)


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_user():
    """Admin create user with any role."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'user').strip()
        gender = request.form.get('gender', '').strip()
        age = request.form.get('age', '').strip()
        height = request.form.get('height', '').strip()
        weight = request.form.get('weight', '').strip()

        errors = []
        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters.')
        if not email or not re.match(EMAIL_REGEX, email):
            errors.append('Invalid email address.')
        elif User.query.filter_by(email=email).first():
            errors.append('Email already in use.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if role not in ['user', 'trainer', 'nutritionist', 'admin']:
            errors.append('Invalid role specified.')

        parsed_age = int(age) if age and age.isdigit() else None
        parsed_height = float(height) if height and height.replace('.', '', 1).isdigit() else None
        parsed_weight = float(weight) if weight and weight.replace('.', '', 1).isdigit() else None

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('admin/user_create.html', name=name, email=email, role=role)

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
        db.session.commit()

        flash(f'User "{name}" ({role}) created successfully!', 'success')
        return redirect(url_for('admin.list_users'))

    return render_template('admin/user_create.html')


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user(user_id):
    """Admin edit user details and role."""
    user = db.get_or_404(User, user_id)
    current_admin = get_current_user()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        role = request.form.get('role', user.role).strip()
        new_password = request.form.get('new_password', '').strip()
        gender = request.form.get('gender', '').strip()
        age = request.form.get('age', '').strip()
        height = request.form.get('height', '').strip()
        weight = request.form.get('weight', '').strip()

        errors = []
        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters.')
        if not email or not re.match(EMAIL_REGEX, email):
            errors.append('Invalid email address.')
        
        # Check duplicate email if changed
        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != user.id:
            errors.append('Email is already taken by another account.')

        # Protect against removing the last administrator
        if user.id == current_admin.id and role != 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                errors.append('Cannot demote the only administrator account.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('admin/user_edit.html', user=user)

        user.name = name
        user.email = email
        user.role = role
        user.gender = gender if gender else None
        user.age = int(age) if age and age.isdigit() else None
        user.height = float(height) if height and height.replace('.', '', 1).isdigit() else None
        user.weight = float(weight) if weight and weight.replace('.', '', 1).isdigit() else None

        if new_password:
            if len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'warning')
            else:
                user.set_password(new_password)

        db.session.commit()
        flash(f'User "{user.name}" updated successfully!', 'success')
        return redirect(url_for('admin.list_users'))

    return render_template('admin/user_edit.html', user=user)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    """Admin delete user account."""
    user = db.get_or_404(User, user_id)
    current_admin = get_current_user()

    if user.id == current_admin.id:
        flash('You cannot delete your own administrator account while logged in.', 'danger')
        return redirect(url_for('admin.list_users'))

    user_name = user.name
    db.session.delete(user)
    db.session.commit()

    flash(f'User "{user_name}" and all associated data deleted successfully.', 'success')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/workouts')
@login_required
@role_required('admin')
def list_workouts():
    """Admin global workout management."""
    workout_type = request.args.get('type', '').strip()
    query = Workout.query

    if workout_type:
        query = query.filter_by(workout_type=workout_type)

    workouts = query.order_by(Workout.workout_date.desc(), Workout.id.desc()).all()
    return render_template('admin/workouts.html', workouts=workouts, workout_type=workout_type)


@admin_bp.route('/workouts/<int:workout_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_workout(workout_id):
    """Admin delete any workout."""
    workout = db.get_or_404(Workout, workout_id)
    db.session.delete(workout)
    db.session.commit()
    flash('Workout record deleted.', 'success')
    return redirect(url_for('admin.list_workouts'))


@admin_bp.route('/goals')
@login_required
@role_required('admin')
def list_goals():
    """Admin global goals management."""
    goals = Goal.query.order_by(Goal.created_at.desc()).all()
    return render_template('admin/goals.html', goals=goals)


@admin_bp.route('/goals/<int:goal_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_goal(goal_id):
    """Admin delete any goal."""
    goal = db.get_or_404(Goal, goal_id)
    db.session.delete(goal)
    db.session.commit()
    flash('Goal record deleted.', 'success')
    return redirect(url_for('admin.list_goals'))


@admin_bp.route('/weights')
@login_required
@role_required('admin')
def list_weights():
    """Admin global weights management."""
    weights = WeightRecord.query.order_by(WeightRecord.date.desc(), WeightRecord.id.desc()).all()
    return render_template('admin/weights.html', weights=weights)


@admin_bp.route('/weights/<int:record_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_weight(record_id):
    """Admin delete any weight log."""
    weight = db.get_or_404(WeightRecord, record_id)
    db.session.delete(weight)
    db.session.commit()
    flash('Weight record deleted.', 'success')
    return redirect(url_for('admin.list_weights'))
