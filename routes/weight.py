from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, WeightRecord
from . import login_required, get_current_user

weight_bp = Blueprint('weight', __name__)

@weight_bp.route('/weight')
@login_required
def history():
    """View weight history logs with BMI and change indications."""
    user = get_current_user()

    records = WeightRecord.query.filter_by(user_id=user.id).order_by(WeightRecord.date.desc(), WeightRecord.id.desc()).all()

    # Enrich records with BMI and delta calculation
    enriched_records = []
    for i, r in enumerate(records):
        bmi_val = r.bmi_for_height(user.height)
        delta = None
        # delta compared to the chronologically prior entry (which is at index i+1 in descending list)
        if i + 1 < len(records):
            delta = round(r.weight - records[i + 1].weight, 1)

        enriched_records.append({
            'record': r,
            'bmi': bmi_val,
            'delta': delta
        })

    # Stats
    current_weight = user.weight
    initial_weight = records[-1].weight if records else current_weight
    total_change = round(current_weight - initial_weight, 1) if (current_weight and initial_weight) else 0.0

    return render_template(
        'weight/history.html',
        records=enriched_records,
        current_weight=current_weight,
        initial_weight=initial_weight,
        total_change=total_change,
        user=user
    )


@weight_bp.route('/weight/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new weight entry."""
    user = get_current_user()

    if request.method == 'POST':
        weight_str = request.form.get('weight', '').strip()
        date_str = request.form.get('date', '').strip()
        notes = request.form.get('notes', '').strip()

        errors = []
        if not weight_str:
            errors.append('Please provide a weight value.')

        parsed_weight = 0.0
        try:
            parsed_weight = float(weight_str)
            if parsed_weight < 20 or parsed_weight > 400:
                errors.append('Weight must be between 20 kg and 400 kg.')
        except ValueError:
            errors.append('Weight must be a valid number.')

        parsed_date = date.today()
        if date_str:
            try:
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Invalid date format.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'weight/add.html',
                weight=weight_str,
                date=date_str,
                notes=notes
            )

        new_record = WeightRecord(
            user_id=user.id,
            weight=parsed_weight,
            date=parsed_date,
            notes=notes if notes else None
        )
        db.session.add(new_record)

        # Update user's current weight if this record is today or most recent
        latest_record = WeightRecord.query.filter_by(user_id=user.id).order_by(WeightRecord.date.desc()).first()
        if not latest_record or parsed_date >= latest_record.date:
            user.weight = parsed_weight

        db.session.commit()
        flash(f'Weight entry of {parsed_weight} kg logged successfully!', 'success')
        return redirect(url_for('weight.history'))

    return render_template(
        'weight/add.html',
        today_date=date.today().strftime('%Y-%m-%d'),
        user=user
    )


@weight_bp.route('/weight/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(record_id):
    """Edit a weight record."""
    record = db.get_or_404(WeightRecord, record_id)
    user = get_current_user()

    if record.user_id != user.id and user.role != 'admin':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('weight.history'))

    if request.method == 'POST':
        weight_str = request.form.get('weight', '').strip()
        date_str = request.form.get('date', '').strip()
        notes = request.form.get('notes', '').strip()

        errors = []
        parsed_weight = record.weight
        try:
            parsed_weight = float(weight_str)
            if parsed_weight < 20 or parsed_weight > 400:
                errors.append('Weight must be between 20 kg and 400 kg.')
        except ValueError:
            errors.append('Weight must be a valid number.')

        parsed_date = record.date
        if date_str:
            try:
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Invalid date format.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('weight/edit.html', record=record)

        record.weight = parsed_weight
        record.date = parsed_date
        record.notes = notes if notes else None

        # Re-sync current weight from latest date
        latest = WeightRecord.query.filter_by(user_id=user.id).order_by(WeightRecord.date.desc(), WeightRecord.id.desc()).first()
        if latest:
            user.weight = latest.weight

        db.session.commit()
        flash('Weight record updated successfully!', 'success')
        return redirect(url_for('weight.history'))

    return render_template('weight/edit.html', record=record)


@weight_bp.route('/weight/<int:record_id>/delete', methods=['POST'])
@login_required
def delete(record_id):
    """Delete a weight record."""
    record = db.get_or_404(WeightRecord, record_id)
    user = get_current_user()

    if record.user_id != user.id and user.role != 'admin':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('weight.history'))

    db.session.delete(record)
    db.session.commit()

    # Re-sync user's current weight from remaining latest record
    latest = WeightRecord.query.filter_by(user_id=user.id).order_by(WeightRecord.date.desc(), WeightRecord.id.desc()).first()
    if latest:
        user.weight = latest.weight
    else:
        user.weight = None
    db.session.commit()

    flash('Weight record deleted.', 'success')
    return redirect(url_for('weight.history'))
