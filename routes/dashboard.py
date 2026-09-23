from datetime import timedelta, date
from flask import Blueprint, render_template, session, redirect, url_for
from models import db, Workout, Goal, WeightRecord, Recommendation
from . import login_required, role_required, get_current_user

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    """Public home / landing page."""
    if 'user_id' in session:
        role = session.get('user_role')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'trainer':
            return redirect(url_for('trainer.dashboard'))
        elif role == 'nutritionist':
            return redirect(url_for('nutritionist.dashboard'))
        return redirect(url_for('dashboard.user_dashboard'))
    return render_template('index.html')


@dashboard_bp.route('/dashboard')
@login_required
@role_required('user')
def user_dashboard():
    """Main dashboard for regular user."""
    user = get_current_user()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    # Metrics calculation
    total_workouts = Workout.query.filter_by(user_id=user.id).count()
    
    # Workouts in the last 7 days
    seven_days_ago = date.today() - timedelta(days=7)
    recent_workouts = Workout.query.filter(
        Workout.user_id == user.id,
        Workout.workout_date >= seven_days_ago
    ).all()
    
    weekly_workouts_count = len(recent_workouts)
    weekly_calories = sum(w.calories_burned for w in recent_workouts)
    total_calories = db.session.query(db.func.sum(Workout.calories_burned)).filter_by(user_id=user.id).scalar() or 0.0
    total_minutes = db.session.query(db.func.sum(Workout.duration)).filter_by(user_id=user.id).scalar() or 0

    # Recent workout logs (top 5)
    latest_workouts = Workout.query.filter_by(user_id=user.id).order_by(Workout.workout_date.desc(), Workout.id.desc()).limit(5).all()

    # Goals summary
    active_goals = Goal.query.filter_by(user_id=user.id, status='ACTIVE').order_by(Goal.target_date.asc()).all()
    completed_goals_count = Goal.query.filter_by(user_id=user.id, status='COMPLETED').count()

    # Weight history (last 5 records)
    recent_weights = WeightRecord.query.filter_by(user_id=user.id).order_by(WeightRecord.date.desc(), WeightRecord.id.desc()).limit(5).all()

    # Guidance recommendations received from trainer or nutritionist
    recommendations = Recommendation.query.filter_by(user_id=user.id).order_by(Recommendation.created_at.desc()).limit(4).all()

    # BMI status
    bmi_val = user.bmi
    bmi_category = user.bmi_category
    bmi_color = user.bmi_badge_color

    return render_template(
        'dashboard.html',
        user=user,
        total_workouts=total_workouts,
        weekly_workouts_count=weekly_workouts_count,
        weekly_calories=round(weekly_calories, 1),
        total_calories=round(total_calories, 1),
        total_minutes=total_minutes,
        latest_workouts=latest_workouts,
        active_goals=active_goals,
        completed_goals_count=completed_goals_count,
        recent_weights=recent_weights,
        recommendations=recommendations,
        bmi=bmi_val,
        bmi_category=bmi_category,
        bmi_color=bmi_color
    )
