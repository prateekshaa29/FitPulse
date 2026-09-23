from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User, Workout, Goal, WeightRecord, Recommendation
from . import login_required, role_required, get_current_user

trainer_bp = Blueprint('trainer', __name__, url_prefix='/trainer')

@trainer_bp.route('/dashboard')
@login_required
@role_required('trainer', 'admin')
def dashboard():
    """Trainer dashboard overview."""
    clients = User.query.filter_by(role='user').order_by(User.name.asc()).all()
    total_clients = len(clients)
    
    # Total workouts logged by all clients
    total_client_workouts = Workout.query.join(User).filter(User.role == 'user').count()
    active_client_goals = Goal.query.join(User).filter(User.role == 'user', Goal.status == 'ACTIVE').count()
    
    # Recommendations given by this trainer
    trainer = get_current_user()
    my_notes = Recommendation.query.filter_by(author_id=trainer.id, note_type='WORKOUT').order_by(Recommendation.created_at.desc()).limit(5).all()

    return render_template(
        'trainer/dashboard.html',
        trainer=trainer,
        clients=clients,
        total_clients=total_clients,
        total_client_workouts=total_client_workouts,
        active_client_goals=active_client_goals,
        my_notes=my_notes
    )


@trainer_bp.route('/users')
@login_required
@role_required('trainer', 'admin')
def list_users():
    """List all client users for trainer review."""
    search = request.args.get('search', '').strip()
    query = User.query.filter_by(role='user')

    if search:
        query = query.filter(
            (User.name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )

    clients = query.order_by(User.name.asc()).all()
    return render_template('trainer/users.html', clients=clients, search=search)


@trainer_bp.route('/users/<int:user_id>')
@login_required
@role_required('trainer', 'admin')
def user_detail(user_id):
    """View client's fitness details, workouts, goals, and existing trainer notes."""
    client = db.get_or_404(User, user_id)
    if client.role != 'user':
        flash('Requested user is not a client.', 'warning')
        return redirect(url_for('trainer.list_users'))

    workouts = Workout.query.filter_by(user_id=client.id).order_by(Workout.workout_date.desc()).all()
    goals = Goal.query.filter_by(user_id=client.id).order_by(Goal.status.asc(), Goal.target_date.asc()).all()
    weight_records = WeightRecord.query.filter_by(user_id=client.id).order_by(WeightRecord.date.desc()).limit(10).all()
    recommendations = Recommendation.query.filter_by(user_id=client.id, note_type='WORKOUT').order_by(Recommendation.created_at.desc()).all()

    total_calories = sum(w.calories_burned for w in workouts)
    total_minutes = sum(w.duration for w in workouts)

    return render_template(
        'trainer/user_detail.html',
        client=client,
        workouts=workouts,
        goals=goals,
        weight_records=weight_records,
        recommendations=recommendations,
        total_calories=round(total_calories, 1),
        total_minutes=total_minutes
    )


@trainer_bp.route('/users/<int:user_id>/recommend', methods=['POST'])
@login_required
@role_required('trainer', 'admin')
def add_recommendation(user_id):
    """Provide a workout recommendation or guidance note for a client."""
    client = db.get_or_404(User, user_id)
    trainer = get_current_user()

    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()

    if not title or not content:
        flash('Title and content are required for workout recommendations.', 'danger')
        return redirect(url_for('trainer.user_detail', user_id=user_id))

    new_rec = Recommendation(
        user_id=client.id,
        author_id=trainer.id,
        note_type='WORKOUT',
        title=title,
        content=content
    )
    db.session.add(new_rec)
    db.session.commit()

    flash(f'Workout recommendation provided to {client.name} successfully!', 'success')
    return redirect(url_for('trainer.user_detail', user_id=user_id))


@trainer_bp.route('/recommendations/<int:rec_id>/delete', methods=['POST'])
@login_required
@role_required('trainer', 'admin')
def delete_recommendation(rec_id):
    """Delete a workout recommendation."""
    rec = db.get_or_404(Recommendation, rec_id)
    trainer = get_current_user()

    if rec.author_id != trainer.id and trainer.role != 'admin':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('trainer.dashboard'))

    user_id = rec.user_id
    db.session.delete(rec)
    db.session.commit()

    flash('Recommendation removed.', 'success')
    return redirect(url_for('trainer.user_detail', user_id=user_id))
