from datetime import date, timedelta
from flask import Blueprint, render_template, jsonify, request
from models import db, Workout, Goal, WeightRecord
from . import login_required, get_current_user

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/progress')
@login_required
def view_progress():
    """Render progress visualization analytics page."""
    user = get_current_user()

    total_workouts = Workout.query.filter_by(user_id=user.id).count()
    total_weights = WeightRecord.query.filter_by(user_id=user.id).count()
    total_goals = Goal.query.filter_by(user_id=user.id).count()

    return render_template(
        'progress.html',
        user=user,
        total_workouts=total_workouts,
        total_weights=total_weights,
        total_goals=total_goals
    )


@progress_bp.route('/api/progress-data')
@login_required
def get_progress_data():
    """Aggregate real database data for Chart.js visualization."""
    user = get_current_user()
    days_param = request.args.get('days', '30')

    # Date filter cutoff
    cutoff_date = None
    if days_param != 'all':
        try:
            days_count = int(days_param)
            cutoff_date = date.today() - timedelta(days=days_count)
        except ValueError:
            cutoff_date = date.today() - timedelta(days=30)

    # 1. Weight history over time (ascending for charts)
    weight_query = WeightRecord.query.filter_by(user_id=user.id)
    if cutoff_date:
        weight_query = weight_query.filter(WeightRecord.date >= cutoff_date)
    weight_records = weight_query.order_by(WeightRecord.date.asc()).all()

    weight_labels = [r.date.strftime('%b %d') for r in weight_records]
    weight_data = [r.weight for r in weight_records]

    # 2. Workouts over time (duration and calories)
    workout_query = Workout.query.filter_by(user_id=user.id)
    if cutoff_date:
        workout_query = workout_query.filter(Workout.workout_date >= cutoff_date)
    workouts = workout_query.order_by(Workout.workout_date.asc()).all()

    # Aggregate by date
    workout_by_date = {}
    for w in workouts:
        d_str = w.workout_date.strftime('%b %d')
        if d_str not in workout_by_date:
            workout_by_date[d_str] = {'duration': 0, 'calories': 0.0, 'count': 0}
        workout_by_date[d_str]['duration'] += w.duration
        workout_by_date[d_str]['calories'] += w.calories_burned
        workout_by_date[d_str]['count'] += 1

    workout_labels = list(workout_by_date.keys())
    workout_durations = [workout_by_date[d]['duration'] for d in workout_labels]
    workout_calories = [workout_by_date[d]['calories'] for d in workout_labels]
    workout_counts = [workout_by_date[d]['count'] for d in workout_labels]

    # 3. Workout Breakdown by Type (all time or filtered)
    type_counts = db.session.query(
        Workout.workout_type,
        db.func.count(Workout.id),
        db.func.sum(Workout.duration)
    ).filter(Workout.user_id == user.id)
    if cutoff_date:
        type_counts = type_counts.filter(Workout.workout_date >= cutoff_date)
    type_counts = type_counts.group_by(Workout.workout_type).all()

    type_labels = [tc[0] for tc in type_counts]
    type_data_counts = [tc[1] for tc in type_counts]
    type_data_durations = [tc[2] or 0 for tc in type_counts]

    # 4. Goals Status Breakdown
    active_goals = Goal.query.filter_by(user_id=user.id, status='ACTIVE').count()
    completed_goals = Goal.query.filter_by(user_id=user.id, status='COMPLETED').count()
    expired_goals = Goal.query.filter_by(user_id=user.id, status='EXPIRED').count()

    return jsonify({
        'weight': {
            'labels': weight_labels,
            'data': weight_data,
            'has_data': len(weight_data) > 0
        },
        'workouts': {
            'labels': workout_labels,
            'durations': workout_durations,
            'calories': workout_calories,
            'counts': workout_counts,
            'has_data': len(workout_labels) > 0
        },
        'types': {
            'labels': type_labels,
            'counts': type_data_counts,
            'durations': type_data_durations,
            'has_data': len(type_labels) > 0
        },
        'goals': {
            'labels': ['Active', 'Completed', 'Expired'],
            'data': [active_goals, completed_goals, expired_goals],
            'has_data': (active_goals + completed_goals + expired_goals) > 0
        }
    })
