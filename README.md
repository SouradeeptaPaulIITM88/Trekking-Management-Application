# Trekking Management Application

A role-based web application for managing trekking activities — built for
**Admin**, **Trek Staff**, and **Trekkers (Users)** to coordinate trek
approvals, staff assignment, bookings, and trekking history in one place.

---

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite (created programmatically via SQLAlchemy models)
- **ORM:** Flask-SQLAlchemy
- **Frontend:** HTML, CSS, Jinja2 templating
- **Auth:** Flask sessions (role-based access control, no external auth library)

---

## Project Structure (MVC)

```
Trekking-Management-Application/
│
├── app.py              # App entry point — Flask setup, DB init, default Admin creation
├── controller.py        # All application routes (Admin / Staff / Trekker) — the "Controller"
├── models.py             # SQLAlchemy models — the "Model"
│
├── templates/            # Jinja2 HTML templates — the "View"
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── admin_dashboard.html
│   ├── admin_staff.html
│   ├── admin_treks.html
│   ├── trek_form.html
│   ├── Booking.html
│   ├── staff_dashboard.html
│   ├── staff_trek.html
│   ├── edit_staff.html
│   ├── user_dashboard.html
│   ├── trek_details.html
│   ├── my_bookings.html
│   ├── edit_trekker.html
│   ├── user_history.html
│   └── ...
│
├── static/
│   ├── main.css          # Custom stylesheet
│   └── background.jpg
│
└── instance/
    └── trekking.sqlite3   # Auto-generated SQLite database (via db.create_all())
```

## MVC Breakdown

**Model** (`models.py`)
SQLAlchemy classes mapping to database tables: `user`, `staff_profile`,
`trekker`, `trek`, `booking`, `trek_history`. Relationships (1:1, 1:M) are
defined via `db.relationship`, and the schema is created entirely in code —
no manual database setup.

**View** (`templates/`)
Jinja2 templates render all pages server-side. `base.html` provides the
shared layout; role-specific templates extend it for Admin, Staff, and
Trekker dashboards. Styling is done with a single custom `main.css` file
(no external CSS framework).

**Controller** (`controller.py`)
Every route handles a specific action — login, registration, trek
management, staff approval, booking, cancellation, history — reading
form data via `request.form`, querying/updating the database through
SQLAlchemy, and returning either a rendered template or a redirect.

---

## Roles & Core Features

### Admin (pre-seeded, no self-registration)
- Dashboard with live counts: total treks, users, staff, bookings
- Create and edit treks; assign staff to treks
- Approve or reject Trek Staff registration requests
- Search staff/users by name or ID
- Blacklist / reactivate users and staff
- View all bookings and trekking history

### Trek Staff (self-registers, needs Admin approval)
- View treks assigned by Admin
- Update available slots and trek status (Open / Closed / Ongoing / Completed)
- View list of participants booked on their treks
- Marking a trek "Completed" auto-generates trek history records

### Trekker / User (self-registers)
- Search and filter available treks by difficulty and location
- Book treks (blocked if trek isn't "Open" or has no slots left)
- Prevented from double-booking the same trek while a booking is active
- View current bookings, cancel active bookings (slot is restored)
- View personal trekking history
- Edit profile details

---

## Getting Started

```bash
# 1. Install dependencies
pip install flask flask-sqlalchemy

# 2. Run the app
python app.py

# 3. Open in browser
http://127.0.0.1:5000/
```

The database (`trekking.sqlite3`) and a default Admin account are created
automatically on first run:

```
Email:    admin@trekking.com
Password: admin123
```

---

## Notes

- All core role-based functionality (auth, trek management, booking,
  history) is implemented per the problem statement's core requirements.
- API endpoints and Bootstrap integration were treated as optional per
  the problem statement and were not implemented in this version.