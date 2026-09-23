from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User, Goal, WeightRecord, Recommendation
from . import login_required, role_required, get_current_user

nutritionist_bp = Blueprint('nutritionist', __name__, url_prefix='/nutritionist')

@nutritionist_bp.route('/dashboard')
@login_required
@role_required('nutritionist', 'admin')
def dashboard():
    """Nutritionist dashboard overview."""
    clients = User.query.filter_by(role='user').order_by(User.name.asc()).all()
    total_clients = len(clients)

    # Calculate BMI distributions
    bmi_dist = {'Underweight': 0, 'Normal weight': 0, 'Overweight': 0, 'Obesity': 0, 'Not Recorded': 0}
    for c in clients:
        bmi_dist[c.bmi_category] = bmi_dist.get(c.bmi_category, 0) + 1

    nutritionist = get_current_user()
    my_notes = Recommendation.query.filter_by(author_id=nutritionist.id, note_type='NUTRITION').order_by(Recommendation.created_at.desc()).limit(5).all()

    return render_template(
        'nutritionist/dashboard.html',
        nutritionist=nutritionist,
        clients=clients,
        total_clients=total_clients,
        bmi_dist=bmi_dist,
        my_notes=my_notes
    )


@nutritionist_bp.route('/users')
@login_required
@role_required('nutritionist', 'admin')
def list_users():
    """List all clients with their BMI and weight metrics for nutritionist review."""
    search = request.args.get('search', '').strip()
    query = User.query.filter_by(role='user')

    if search:
        query = query.filter(
            (User.name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )

    clients = query.order_by(User.name.asc()).all()
    return render_template('nutritionist/users.html', clients=clients, search=search)


@nutritionist_bp.route('/users/<int:user_id>')
@login_required
@role_required('nutritionist', 'admin')
def user_detail(user_id):
    """View client's weight logs, BMI trends, dietary goals, and existing nutrition notes."""
    client = db.get_or_404(User, user_id)
    if client.role != 'user':
        flash('Requested user is not a client.', 'warning')
        return redirect(url_for('nutritionist.list_users'))

    weight_records = WeightRecord.query.filter_by(user_id=client.id).order_by(WeightRecord.date.desc()).all()
    goals = Goal.query.filter_by(user_id=client.id).order_by(Goal.status.asc(), Goal.target_date.asc()).all()
    recommendations = Recommendation.query.filter_by(user_id=client.id, note_type='NUTRITION').order_by(Recommendation.created_at.desc()).all()

    # Calculate initial vs current weight
    current_weight = client.weight
    initial_weight = weight_records[-1].weight if weight_records else current_weight
    weight_change = round(current_weight - initial_weight, 1) if (current_weight and initial_weight) else 0.0

    return render_template(
        'nutritionist/user_detail.html',
        client=client,
        weight_records=weight_records,
        goals=goals,
        recommendations=recommendations,
        current_weight=current_weight,
        initial_weight=initial_weight,
        weight_change=weight_change
    )


@nutritionist_bp.route('/users/<int:user_id>/recommend', methods=['POST'])
@login_required
@role_required('nutritionist', 'admin')
def add_recommendation(user_id):
    """Provide a nutrition/diet recommendation for a client."""
    client = db.get_or_404(User, user_id)
    nutritionist = get_current_user()

    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()

    if not title or not content:
        flash('Title and advice content are required for nutrition recommendations.', 'danger')
        return redirect(url_for('nutritionist.user_detail', user_id=user_id))

    new_rec = Recommendation(
        user_id=client.id,
        author_id=nutritionist.id,
        note_type='NUTRITION',
        title=title,
        content=content
    )
    db.session.add(new_rec)
    db.session.commit()

    flash(f'Nutrition guidance sent to {client.name} successfully!', 'success')
    return redirect(url_for('nutritionist.user_detail', user_id=user_id))


@nutritionist_bp.route('/recommendations/<int:rec_id>/delete', methods=['POST'])
@login_required
@role_required('nutritionist', 'admin')
def delete_recommendation(rec_id):
    """Delete a nutrition recommendation."""
    rec = db.get_or_404(Recommendation, rec_id)
    nutritionist = get_current_user()

    if rec.author_id != nutritionist.id and nutritionist.role != 'admin':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('nutritionist.dashboard'))

    user_id = rec.user_id
    db.session.delete(rec)
    db.session.commit()

    flash('Nutrition recommendation removed.', 'success')
    return redirect(url_for('nutritionist.user_detail', user_id=user_id))
