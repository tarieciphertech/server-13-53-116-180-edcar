from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(256))
    role = db.Column(db.String(20))  # admin, agent
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Float)
    proof_file = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    user = db.relationship('User', backref='payments', foreign_keys=[user_id])


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    property_type = db.Column(db.String(50))   # house, apartment, land, commercial, office
    listing_type = db.Column(db.String(20))    # sale, rent, lease
    price = db.Column(db.String(100))
    location = db.Column(db.String(200))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100), default='Zimbabwe')
    bedrooms = db.Column(db.Integer, nullable=True)
    bathrooms = db.Column(db.Integer, nullable=True)
    size_sqm = db.Column(db.String(50), nullable=True)
    features = db.Column(db.Text, nullable=True)   # comma-separated: pool, garage, garden etc
    images = db.relationship('PropertyImage', backref='property', lazy=True, cascade='all, delete-orphan')
    is_managed = db.Column(db.Boolean, default=False)  # Edcar managed = free listing
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='properties', foreign_keys=[user_id])

    @property
    def main_image(self):
        if self.images:
            return self.images[0].filename
        return None


class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    filename = db.Column(db.String(200))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # residential, commercial, renovation
    location = db.Column(db.String(200))
    status = db.Column(db.String(50))     # ongoing, completed, upcoming
    image_file = db.Column(db.String(200), nullable=True)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CarRental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.String(10))
    color = db.Column(db.String(50))
    price_per_day = db.Column(db.String(50))
    seats = db.Column(db.Integer)
    transmission = db.Column(db.String(20))  # manual, automatic
    fuel_type = db.Column(db.String(20))     # petrol, diesel, electric
    features = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(200), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visitor_name = db.Column(db.String(100))
    visitor_email = db.Column(db.String(120))
    visitor_phone = db.Column(db.String(20))
    inquiry_type = db.Column(db.String(20))   # property, car, project, general
    reference_id = db.Column(db.Integer, nullable=True)
    message = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_handled = db.Column(db.Boolean, default=False)
