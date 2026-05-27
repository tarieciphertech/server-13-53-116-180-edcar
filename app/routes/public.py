from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory
from app.models import db, Property, Project, CarRental, Inquiry
from app.notifications import notify_new_inquiry
from datetime import datetime
import os

public = Blueprint('public', __name__)


@public.route('/')
def home():
    featured = Property.query.filter_by(is_published=True, is_featured=True).limit(6).all()
    for_sale = Property.query.filter_by(is_published=True, listing_type='sale').order_by(Property.submitted_at.desc()).limit(4).all()
    for_rent = Property.query.filter_by(is_published=True, listing_type='rent').order_by(Property.submitted_at.desc()).limit(4).all()
    projects = Project.query.filter_by(is_published=True).order_by(Project.created_at.desc()).limit(3).all()
    cars = CarRental.query.filter_by(is_published=True, is_available=True).limit(3).all()
    return render_template('public/home.html',
                           featured=featured,
                           for_sale=for_sale,
                           for_rent=for_rent,
                           projects=projects,
                           cars=cars)


@public.route('/properties')
def properties():
    listing_type = request.args.get('type', '')
    property_type = request.args.get('property_type', '')
    city = request.args.get('city', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')

    query = Property.query.filter_by(is_published=True)
    if listing_type:
        query = query.filter_by(listing_type=listing_type)
    if property_type:
        query = query.filter_by(property_type=property_type)
    if city:
        query = query.filter(Property.city.ilike(f'%{city}%'))

    all_properties = query.order_by(Property.is_featured.desc(), Property.submitted_at.desc()).all()
    cities = db.session.query(Property.city).filter_by(is_published=True).distinct().all()
    return render_template('public/properties.html',
                           properties=all_properties,
                           cities=[c[0] for c in cities],
                           listing_type=listing_type,
                           property_type=property_type,
                           city=city)


@public.route('/properties/<int:property_id>')
def property_detail(property_id):
    prop = Property.query.get_or_404(property_id)
    similar = Property.query.filter_by(
        is_published=True,
        listing_type=prop.listing_type,
        city=prop.city
    ).filter(Property.id != prop.id).limit(3).all()
    return render_template('public/property_detail.html', prop=prop, similar=similar)


@public.route('/projects')
def projects():
    all_projects = Project.query.filter_by(is_published=True).order_by(Project.created_at.desc()).all()
    return render_template('public/projects.html', projects=all_projects)


@public.route('/car-rental')
def car_rental():
    cars = CarRental.query.filter_by(is_published=True).order_by(CarRental.is_available.desc()).all()
    return render_template('public/car_rental.html', cars=cars)


@public.route('/contact')
def contact():
    return render_template('public/contact.html')


@public.route('/inquire', methods=['POST'])
def inquire():
    inquiry = Inquiry(
        visitor_name=request.form.get('visitor_name'),
        visitor_email=request.form.get('visitor_email'),
        visitor_phone=request.form.get('visitor_phone'),
        inquiry_type=request.form.get('inquiry_type'),
        reference_id=request.form.get('reference_id'),
        message=request.form.get('message')
    )
    db.session.add(inquiry)
    db.session.commit()
    reference = request.form.get('reference_title', 'a listing')
    notify_new_inquiry(inquiry, reference)
    flash('Your inquiry has been sent! We will contact you shortly.', 'success')
    return redirect(request.referrer or url_for('public.home'))


@public.route('/uploads/<path:filename>')
def uploaded_file(filename):
    upload_folder = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'static', 'uploads'
    )
    return send_from_directory(upload_folder, filename)
