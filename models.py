from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class user(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String, nullable=False)  # changed True -> False, signup form now always collects this
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False , default="Active")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 1:1 -> staff_profile (only populated if role == "Staff")
    staff_profile = db.relationship(
        'staff_profile', backref='user', uselist=False, cascade="all, delete-orphan"
    )

    # 1:1 -> trekker (only populated if role == "Trekker")
    trekker = db.relationship(
        'trekker', backref='user', uselist=False, cascade="all, delete-orphan"
    )


class staff_profile(db.Model):
    staff_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    experience_years = db.Column(db.Integer)
    dino_speciality = db.Column(db.String)
    approval_status = db.Column(db.String, nullable=False, default="Pending")
    contact = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 1:M -> trek (one staff member can be assigned to many treks)
    treks = db.relationship('trek', backref='assigned_staff', lazy=True)


class trekker(db.Model):
    trekker_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    emergency_contact = db.Column(db.String)
    address = db.Column(db.String)
    preferred_difficulty = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 1:M -> booking (one trekker can make many bookings)
    bookings = db.relationship('booking', backref='trekker', lazy=True)


class trek(db.Model):
    trek_id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.String, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False, default=0)    
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('staff_profile.staff_id'))
    status = db.Column(db.String, nullable=False, default="Pending")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 1:M -> booking (one trek can have many bookings)
    bookings = db.relationship('booking', backref='trek', lazy=True)


class booking(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    trekker_id = db.Column(db.Integer, db.ForeignKey('trekker.trekker_id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.trek_id'), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    booking_status = db.Column(db.String, nullable=False, default="Booked")
    payment_status = db.Column(db.String, nullable=False, default="Unpaid")

    # 1:1 -> trek_history (a booking has at most one history record)
    trek_history = db.relationship(
        'trek_history', backref='booking', uselist=False, cascade="all, delete-orphan"
    )


class trek_history(db.Model):
    history_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.booking_id'), nullable=False)
    completed_on = db.Column(db.DateTime, default=datetime.utcnow)
    remarks = db.Column(db.String)
    final_status = db.Column(db.String, nullable=False)
