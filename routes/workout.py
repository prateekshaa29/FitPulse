from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Workout
from . import login_required, get_current_user

workout_bp = Blueprint('workout', __name__)

WORKOUT_TYPES = [
    'Running',
    'Cycling',
    'Walking',
    'Strength Training',
    'Yoga',
    'Cardio',
    'Swimming',
    'HIIT',
    'Pilates',
    'Other'
]

@workout_bp.route('/workouts')
@login_required
def history():
    """View workout history with filtering."""
    user = get_current_user()
    workout_type_filter = request.args.get('type', '').strip()
    search_query = request.args.get('search', '').strip()

    query = Workout.query.filter_by(user_id=user.id)

    if workout_type_filter:
        query = query.filter_by(workout_type=workout_type_filter)

    if search_query:
        query = query.filter(
            (Workout.exercise_name.ilike(f'%{search_query}%')) |
            (Workout.notes.ilike(f'%{search_query}%'))
        )

    workouts = query.order_by(Workout.workout_date.desc(), Workout.id.desc()).all()

    # Aggregate stats for this user
    total_workouts = len(workouts)
    total_duration = sum(w.duration for w in workouts)
    total_calories = sum(w.calories_burned for w in workouts)

    return render_template(
        'workouts/history.html',
        workouts=workouts,
        workout_types=WORKOUT_TYPES,
        selected_type=workout_type_filter,
        search_query=search_query,
        total_workouts=total_workouts,
        total_duration=total_duration,
        total_calories=round(total_calories, 1)
    )


@workout_bp.route('/workouts/add', methods=['GET', 'POST'])
@login_required
def add():
    """Record a new workout entry."""
    user = get_current_user()

    if request.method == 'POST':
        workout_type = request.form.get('workout_type', '').strip()
        exercise_name = request.form.get('exercise_name', '').strip()
        duration = request.form.get('duration', '').strip()
        sets = request.form.get('sets', '0').strip()
        repetitions = request.form.get('repetitions', '0').strip()
        calories_burned = request.form.get('calories_burned', '0').strip()
        workout_date_str = request.form.get('workout_date', '').strip()
        notes = request.form.get('notes', '').strip()

        errors = []
        if not workout_type:
            errors.append('Please select a workout type.')
        if not exercise_name or len(exercise_name) < 2:
            errors.append('Please provide an exercise or workout name.')

        parsed_duration = 0
        try:
            parsed_duration = int(duration)
            if parsed_duration <= 0 or parsed_duration > 1440:
                errors.append('Duration must be between 1 and 1440 minutes.')
        except ValueError:
            errors.append('Duration must be a valid integer in minutes.')

        parsed_sets = 0
        if sets:
            try:
                parsed_sets = int(sets)
                if parsed_sets < 0:
                    errors.append('Sets cannot be negative.')
            except ValueError:
                errors.append('Sets must be an integer.')

        parsed_reps = 0
        if repetitions:
            try:
                parsed_reps = int(repetitions)
                if parsed_reps < 0:
                    errors.append('Repetitions cannot be negative.')
            except ValueError:
                errors.append('Repetitions must be an integer.')

        parsed_calories = 0.0
        if calories_burned:
            try:
                parsed_calories = float(calories_burned)
                if parsed_calories < 0:
                    errors.append('Calories burned cannot be negative.')
            except ValueError:
                errors.append('Calories burned must be a valid number.')

        parsed_date = date.today()
        if workout_date_str:
            try:
                parsed_date = datetime.strptime(workout_date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Invalid workout date format. Use YYYY-MM-DD.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'workouts/add.html',
                workout_types=WORKOUT_TYPES,
                workout_type=workout_type,
                exercise_name=exercise_name,
                duration=duration,
                sets=sets,
                repetitions=repetitions,
                calories_burned=calories_burned,
                workout_date=workout_date_str,
                notes=notes
            )

        new_workout = Workout(
            user_id=user.id,
            workout_type=workout_type,
            exercise_name=exercise_name,
            duration=parsed_duration,
            sets=parsed_sets,
            repetitions=parsed_reps,
            calories_burned=parsed_calories,
            workout_date=parsed_date,
            notes=notes if notes else None
        )
        db.session.add(new_workout)
        db.session.commit()

        flash(f'Workout "{exercise_name}" logged successfully!', 'success')
        return redirect(url_for('workout.history'))

    return render_template(
        'workouts/add.html',
        workout_types=WORKOUT_TYPES,
        today_date=date.today().strftime('%Y-%m-%d')
    )


@workout_bp.route('/workouts/<int:workout_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(workout_id):
    """Edit an existing workout entry."""
    workout = db.get_or_404(Workout, workout_id)
    user = get_current_user()

    # RBAC: Only owner or admin can edit
    if workout.user_id != user.id and user.role != 'admin':
        flash('You are not authorized to edit this workout.', 'danger')
        return redirect(url_for('workout.history'))

    if request.method == 'POST':
        workout_type = request.form.get('workout_type', '').strip()
        exercise_name = request.form.get('exercise_name', '').strip()
        duration = request.form.get('duration', '').strip()
        sets = request.form.get('sets', '0').strip()
        repetitions = request.form.get('repetitions', '0').strip()
        calories_burned = request.form.get('calories_burned', '0').strip()
        workout_date_str = request.form.get('workout_date', '').strip()
        notes = request.form.get('notes', '').strip()

        errors = []
        if not workout_type:
            errors.append('Please select a workout type.')
        if not exercise_name or len(exercise_name) < 2:
            errors.append('Please provide an exercise name.')

        parsed_duration = 0
        try:
            parsed_duration = int(duration)
            if parsed_duration <= 0 or parsed_duration > 1440:
                errors.append('Duration must be between 1 and 1440 minutes.')
        except ValueError:
            errors.append('Duration must be a valid integer.')

        parsed_sets = 0
        if sets:
            try:
                parsed_sets = int(sets)
                if parsed_sets < 0:
                    errors.append('Sets cannot be negative.')
            except ValueError:
                errors.append('Sets must be an integer.')

        parsed_reps = 0
        if repetitions:
            try:
                parsed_reps = int(repetitions)
                if parsed_reps < 0:
                    errors.append('Repetitions cannot be negative.')
            except ValueError:
                errors.append('Repetitions must be an integer.')

        parsed_calories = 0.0
        if calories_burned:
            try:
                parsed_calories = float(calories_burned)
                if parsed_calories < 0:
                    errors.append('Calories cannot be negative.')
            except ValueError:
                errors.append('Calories must be a number.')

        parsed_date = workout.workout_date
        if workout_date_str:
            try:
                parsed_date = datetime.strptime(workout_date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Invalid date format.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('workouts/edit.html', workout=workout, workout_types=WORKOUT_TYPES)

        workout.workout_type = workout_type
        workout.exercise_name = exercise_name
        workout.duration = parsed_duration
        workout.sets = parsed_sets
        workout.repetitions = parsed_reps
        workout.calories_burned = parsed_calories
        workout.workout_date = parsed_date
        workout.notes = notes if notes else None

        db.session.commit()
        flash('Workout updated successfully!', 'success')
        return redirect(url_for('workout.history'))

    return render_template('workouts/edit.html', workout=workout, workout_types=WORKOUT_TYPES)


@workout_bp.route('/workouts/<int:workout_id>/delete', methods=['POST'])
@login_required
def delete(workout_id):
    """Delete a workout entry."""
    workout = db.get_or_404(Workout, workout_id)
    user = get_current_user()

    if workout.user_id != user.id and user.role != 'admin':
        flash('You are not authorized to delete this workout.', 'danger')
        return redirect(url_for('workout.history'))

    db.session.delete(workout)
    db.session.commit()
    flash('Workout record deleted successfully.', 'success')
    return redirect(url_for('workout.history'))
