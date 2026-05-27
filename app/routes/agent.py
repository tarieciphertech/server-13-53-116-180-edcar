from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, Payment, Property, PropertyImage
from app.notifications import notify_payment_uploaded, notify_property_submitted
import os

agent = Blueprint('agent', __name__, url_prefix='/agent')


def save_file(file, subfolder):
    filename = secure_filename(file.filename)
    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    file.save(path)
    return os.path.join(subfolder, filename)


@agent.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_bp.dashboard'))
    payment = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.submitted_at.desc()).first()
    my_properties = Property.query.filter_by(user_id=current_user.id).order_by(Property.submitted_at.desc()).all()
    return render_template('agent/dashboard.html',
                           payment=payment,
                           properties=my_properties,
                           payment_details=current_app.config['PAYMENT_DETAILS'],
                           listing_fee=current_app.config['LISTING_FEE'])


@agent.route('/upload-proof', methods=['POST'])
@login_required
def upload_proof():
    file = request.files.get('proof')
    if not file or file.filename == '':
        flash('Please select a payment proof file.', 'danger')
        return redirect(url_for('agent.dashboard'))

    filepath = save_file(file, 'proofs')
    existing = Payment.query.filter_by(user_id=current_user.id).first()
    if existing:
        existing.proof_file = filepath
        existing.status = 'pending'
    else:
        payment = Payment(
            user_id=current_user.id,
            amount=current_app.config['LISTING_FEE'],
            proof_file=filepath
        )
        db.session.add(payment)
    db.session.commit()
    notify_payment_uploaded(current_user, current_app.config['LISTING_FEE'])
    flash('Payment proof uploaded! Admin will confirm shortly.', 'success')
    return redirect(url_for('agent.dashboard'))


@agent.route('/submit-property', methods=['POST'])
@login_required
def submit_property():
    if not current_user.is_approved:
        flash('Your account must be activated before listing properties.', 'warning')
        return redirect(url_for('agent.dashboard'))

    prop = Property(
        user_id=current_user.id,
        title=request.form.get('title'),
        description=request.form.get('description'),
        property_type=request.form.get('property_type'),
        listing_type=request.form.get('listing_type'),
        price=request.form.get('price'),
        location=request.form.get('location'),
        city=request.form.get('city'),
        country=request.form.get('country', 'Zimbabwe'),
        bedrooms=request.form.get('bedrooms') or None,
        bathrooms=request.form.get('bathrooms') or None,
        size_sqm=request.form.get('size_sqm'),
        features=request.form.get('features'),
        is_managed=False
    )
    db.session.add(prop)
    db.session.flush()

    images = request.files.getlist('images')
    for img in images:
        if img and img.filename:
            filepath = save_file(img, 'properties')
            image = PropertyImage(property_id=prop.id, filename=filepath)
            db.session.add(image)

    db.session.commit()
    notify_property_submitted(current_user, prop)
    flash('Property submitted! Admin will review and publish it shortly.', 'success')
    return redirect(url_for('agent.dashboard'))
