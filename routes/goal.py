from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Goal
from . import login_required, get_current_user

goal_bp = Blueprint('goal', __name__)

GOAL_TYPES = [
    'Lose Weight',
    'Gain Weight',
    'Run Distance',
    'Workout Frequency',
    'Improve Strength',
    'Burn Calories',
    'Build Muscle',
    'General Fitness'
]

@goal_bp.route('/goals')
@login_required
def view_goals():
    """View user goals with status filtering."""
    user = get_current_user()
    status_filter = request.args.get('status', 'ALL').upper()

    query = Goal.query.filter_by(user_id=user.id)
    if status_filter in ['ACTIVE', 'COMPLETED', 'EXPIRED']:
        query = query.filter_by(status=status_filter)

    goals = query.order_by(Goal.status.asc(), Goal.target_date.asc()).all()

    total_goals = Goal.query.filter_by(user_id=user.id).count()
    active_count = Goal.query.filter_by(user_id=user.id, status='ACTIVE').count()
    completed_count = Goal.query.filter_by(user_id=user.id, status='COMPLETED').count()

    return render_template(
        'goals/view.html',
        goals=goals,
        current_status=status_filter,
        total_goals=total_goals,
        active_count=active_count,
        completed_count=completed_count
    )


@goal_bp.route('/goals/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new fitness goal."""
    user = get_current_user()

    if request.method == 'POST':
        goal_type = request.form.get('goal_type', '').strip()
        target_value = request.form.get('target_value', '').strip()
        current_value = request.form.get('current_value', '').strip()
        start_date_str = request.form.get('start_date', '').strip()
        target_date_str = request.form.get('target_date', '').strip()
        description = request.form.get('description', '').strip()

        errors = []
        if not goal_type:
            errors.append('Please select a goal type.')
        if not target_value:
            errors.append('Please provide a target value (e.g., "70 kg" or "5 days/week").')

        start_date = date.today()
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Invalid start date format.')

        if not target_date_str:
            errors.append('Please select a target completion date.')
        else:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                if target_date < start_date:
                    errors.append('Target date cannot be earlier than the start date.')
            except ValueError:
                errors.append('Invalid target date format.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'goals/add.html',
                goal_types=GOAL_TYPES,
                goal_type=goal_type,
                target_value=target_value,
                current_value=current_value,
                start_date=start_date_str,
                target_date=target_date_str,
                description=description
            )

        new_goal = Goal(
            user_id=user.id,
            goal_type=goal_type,
            target_value=target_value,
            current_value=current_value if current_value else None,
            start_date=start_date,
            target_date=target_date,
            status='ACTIVE',
            description=description if description else None
        )
        db.session.add(new_goal)
        db.session.commit()

        flash(f'Goal "{goal_type}" added successfully!', 'success')
        return redirect(url_for('goal.view_goals'))

    return render_template(
        'goals/add.html',
        goal_types=GOAL_TYPES,
        today_date=date.today().strftime('%Y-%m-%d')
    )


@goal_bp.route('/goals/<int:goal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(goal_id):
    """Edit an existing goal."""
    goal = db.get_or_404(Goal, goal_id)
    user = get_current_user()

    if goal.user_id != user.id and user.role != 'admin':
        flash('You are not authorized to edit this goal.', 'danger')
        return redirect(url_for('goal.view_goals'))

    if request.method == 'POST':
        goal_type = request.form.get('goal_type', '').strip()
        target_value = request.form.get('target_value', '').strip()
        current_value = request.form.get('current_value', '').strip()
        start_date_str = request.form.get('start_date', '').strip()
        target_date_str = request.form.get('target_date', '').strip()
        status = request.form.get('status', 'ACTIVE').strip()
        description = request.form.get('description', '').strip()

        errors = []
        if not goal_type:
            errors.append('Please select a goal type.')
        if not target_value:
            errors.append('Please provide a target value.')

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else goal.start_date
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date() if target_date_str else goal.target_date
            if target_date < start_date:
                errors.append('Target date cannot be earlier than start date.')
        except ValueError:
            errors.append('Invalid date format.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('goals/edit.html', goal=goal, goal_types=GOAL_TYPES)

        goal.goal_type = goal_type
        goal.target_value = target_value
        goal.current_value = current_value if current_value else None
        goal.start_date = start_date
        goal.target_date = target_date
        goal.status = status
        goal.description = description if description else None

        db.session.commit()
        flash('Goal updated successfully!', 'success')
        return redirect(url_for('goal.view_goals'))

    return render_template('goals/edit.html', goal=goal, goal_types=GOAL_TYPES)


@goal_bp.route('/goals/<int:goal_id>/status', methods=['POST'])
@login_required
def toggle_status(goal_id):
    """Toggle goal status (ACTIVE / COMPLETED)."""
    goal = db.get_or_404(Goal, goal_id)
    user = get_current_user()

    if goal.user_id != user.id and user.role != 'admin':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('goal.view_goals'))

    if goal.status == 'ACTIVE':
        goal.status = 'COMPLETED'
        flash(f'Congratulations! Goal "{goal.goal_type}" marked as Completed! 🎉', 'success')
    else:
        goal.status = 'ACTIVE'
        flash(f'Goal "{goal.goal_type}" set to Active.', 'info')

    db.session.commit()
    return redirect(url_for('goal.view_goals'))


@goal_bp.route('/goals/<int:goal_id>/delete', methods=['POST'])
@login_required
def delete(goal_id):
    """Delete a goal."""
    goal = db.get_or_404(Goal, goal_id)
    user = get_current_user()

    if goal.user_id != user.id and user.role != 'admin':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('goal.view_goals'))

    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted successfully.', 'success')
    return redirect(url_for('goal.view_goals'))
