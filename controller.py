from flask import current_app as  app
from flask import render_template , request , redirect , url_for , session
from models import *
from datetime import datetime , timedelta

@app.route("/")
def home():
 return render_template("index.html")


@app.route("/login/" , methods=["GET","POST"])
def signin():
  if request.method == "POST":
    email=request.form.get("email-id")
    pwd=request.form.get("password")
    matched_user=user.query.filter_by(email=email , password=pwd).first()

    if not matched_user:
      return render_template("login.html", error_msg="Invalid email or password")

    if matched_user.status == "Blacklisted":
      return render_template("login.html", error_msg="Your account has been blacklisted")

    # Staff must be approved by Admin before they can log in
    if matched_user.role == "Staff":
      if not matched_user.staff_profile or matched_user.staff_profile.approval_status != "Approved":
        return render_template("login.html", error_msg="Your staff account is pending Admin approval")

    # remember who is logged in, so other pages know the role/id (no Flask-Login used, kept simple)
    session['uid'] = matched_user.user_id
    session['role'] = matched_user.role
    session['name'] = matched_user.full_name

    if matched_user.role == "Admin":
      return redirect(url_for('admin_console'))
    elif matched_user.role == "Staff":
      return redirect(url_for('staff_dashboard'))
    else:
      return redirect(url_for('user_dashboard'))

  return render_template("login.html")


@app.route("/logout")
def logout():
  session.clear()
  return redirect(url_for('signin'))


@app.route("/register" , methods=["GET","POST"])
def register():
   if request.method == "POST":
      full_name=request.form.get("full_name")
      email=request.form.get("email-id")
      pwd=request.form.get("password")
      role=request.form.get("uType")

      matched_user=user.query.filter_by(email=email).first()
      if matched_user :
        return render_template("signup.html",error_msg="Sorry email is aldready used")

      if role not in ("Staff","Trekker"):
        return render_template("signup.html",error_msg="Please select a valid user type")

      uc = user(full_name=full_name, email=email , password=pwd , role=role)
      db.session.add(uc)
      db.session.commit()  

      if role == "Staff":
        sp = staff_profile(
          user_id=uc.user_id,
          dino_speciality=request.form.get("dino_speciality"),
          experience_years=request.form.get("experience_years") or 0,
          contact=request.form.get("contact")
        )
        db.session.add(sp)
      else:
        tk = trekker(
          user_id=uc.user_id,
          address=request.form.get("address"),
          emergency_contact=request.form.get("emergency_contact"),
          preferred_difficulty=request.form.get("preferred_difficulty")
        )
        db.session.add(tk)

      db.session.commit()
      return redirect(url_for('signin'))

   return render_template("signup.html")


# ================= ADMIN =================

@app.route("/admin/")
def admin_console():
  if session.get('role') != 'Admin':
    return redirect(url_for('signin'))

  # search staff/users by name or ID - was missing before
  q = request.args.get('q', '')
  staff_query = user.query.filter_by(role="Staff")
  trekker_query = user.query.filter_by(role="Trekker")
  if q:
    if q.isdigit():
      staff_query = staff_query.filter_by(user_id=int(q))
      trekker_query = trekker_query.filter_by(user_id=int(q))
    else:
      staff_query = staff_query.filter(user.full_name.contains(q))
      trekker_query = trekker_query.filter(user.full_name.contains(q))

  staff_list = staff_query.all()
  trekker_list = trekker_query.all()
  recent_bookings = booking.query.order_by(booking.booking_date.desc()).limit(5).all()

  return render_template("admin_dashboard.html",
    total_treks=trek.query.count(),
    total_users=user.query.filter_by(role="Trekker").count(),
    total_staff=user.query.filter_by(role="Staff").count(),
    total_bookings=booking.query.count(),
    staff_list=staff_list,
    trekker_list=trekker_list,
    recent_bookings=recent_bookings,
    q=q)

#Blacklisting user/staff
@app.route("/toggle_status/<int:user_id>", methods=["POST"])
def toggle_status(user_id):
  if session.get('role') != 'Admin':
    return redirect(url_for('signin'))
  target = user.query.get(user_id)
  if target:
    target.status = "Blacklisted" if target.status == "Active" else "Active"
    db.session.commit()
  return redirect(url_for('admin_console'))

@app.route("/admin/bookings")
def all_bookings():
  if session.get('role') != 'Admin':
    return redirect(url_for('signin'))
  q = request.args.get('q' , '')
  bookings_query = booking.query
  if q:
    bookings_query = bookings_query.join(trekker).join(user).filter(user.full_name.contains(q))
  bookings_list = bookings_query.order_by(booking.booking_date.desc()).all()
  return render_template("admin_bookings.html", bookings_list=bookings_list, q=q)

@app.route("/admin/history")
def admin_history():
  if session.get('role') != 'Admin':
    return redirect(url_for('signin'))
  history_list = trek_history.query.order_by(trek_history.completed_on.desc()).all()
  return render_template("admin_history.html" , hsitory_list = history_list)

@app.route("/admin/booking/<int:booking_id>")
def booking_detail(booking_id):
  if session.get('role') != 'Admin':
    return redirect(url_for('signin'))
  this_booking = booking.query.get(booking_id)
  return render_template("Booking.html", this_booking=this_booking)

#Adding Trek

@app.route("/admin/treks")
def admin_treks():
  if session.get('role') != 'Admin':
    return redirect(url_for('signin'))
  q = request.args.get('q', '')
  if q:
    treks_list = trek.query.filter(trek.trek_name.contains(q)).all()
  else:
    treks_list = trek.query.all()
  return render_template("admin_treks.html", treks_list=treks_list, q=q)


@app.route("/admin/trek_form", methods=["GET","POST"])
def trek_form():
  if session.get('role') != 'Admin':
    return redirect(url_for('signin'))

  trek_id = request.args.get('trek_id')
  edit_trek = trek.query.get(trek_id) if trek_id else None
  staff_list = staff_profile.query.filter_by(approval_status="Approved").all()

  if request.method == "POST":
    if edit_trek:
      edit_trek.trek_name = request.form.get("trek_name")
      edit_trek.location = request.form.get("location")
      edit_trek.difficulty = request.form.get("difficulty")
      edit_trek.duration_days = request.form.get("duration_days")
      edit_trek.start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
      edit_trek.end_date = edit_trek.start_date + timedelta(days=int(edit_trek.duration_days))
      edit_trek.available_slots = request.form.get("available_slots")
      edit_trek.assigned_staff_id = request.form.get("assigned_staff_id") or None
      edit_trek.status = request.form.get("status")
      edit_trek.price = request.form.get("price") or 0
    else:
      new_start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
      new_duration = int(request.form.get("duration_days"))
      new_trek = trek(
        trek_name=request.form.get("trek_name"),
        location=request.form.get("location"),
        difficulty=request.form.get("difficulty"),
        duration_days=new_duration,
        start_date=new_start_date,
        end_date=new_start_date + timedelta(days=new_duration),
        available_slots=request.form.get("available_slots"),
        assigned_staff_id=request.form.get("assigned_staff_id") or None,
        status=request.form.get("status"),
        price=request.form.get("price") or 0
      )
      db.session.add(new_trek)

    db.session.commit()
    return redirect(url_for('admin_treks'))

  return render_template("trek_form.html", edit_trek=edit_trek, staff_list=staff_list)


@app.route("/admin/staff")
def admin_staff():
  if session.get('role') != 'Admin':
    return redirect(url_for('signin'))
  tab = request.args.get('tab', 'Pending')
  staff_list = staff_profile.query.filter_by(approval_status=tab).all()
  return render_template("admin_staff.html", staff_list=staff_list, tab=tab)


@app.route("/admin/staff/approve/<int:staff_id>", methods=["POST"])
def approve_staff(staff_id):
  if session.get('role') != 'Admin':
    return redirect(url_for('signin'))
  s = staff_profile.query.get(staff_id)
  if s:
    s.approval_status = "Approved"
    db.session.commit()
  return redirect(url_for('admin_staff', tab='Pending'))


@app.route("/admin/staff/reject/<int:staff_id>", methods=["POST"])
def reject_staff(staff_id):
  if session.get('role') != 'Admin':
    return redirect(url_for('signin'))
  s = staff_profile.query.get(staff_id)
  if s:
    s.approval_status = "Rejected"
    db.session.commit()
  return redirect(url_for('admin_staff', tab='Pending'))


# ================= TREK STAFF =================

@app.route("/staff/")
def staff_dashboard():
  if session.get('role') != 'Staff':
    return redirect(url_for('signin'))
  my_profile = staff_profile.query.filter_by(user_id=session['uid']).first()
  my_treks = my_profile.treks if my_profile else []
  return render_template("staff_dashboard.html", my_treks=my_treks)

#Staff overseeing the trek 
@app.route("/staff/trek/<int:trek_id>", methods=["GET","POST"])
def staff_trek(trek_id):
  if session.get('role') != 'Staff':
    return redirect(url_for('signin'))
  this_trek = trek.query.get(trek_id)
  my_profile = staff_profile.query.filter_by(user_id=session['uid']).first()

  # only the staff member this trek is assigned to can manage it
  if not this_trek or not my_profile or this_trek.assigned_staff_id != my_profile.staff_id:
    return redirect(url_for('staff_dashboard'))

  if request.method == "POST":
    if this_trek.status == "Completed":
      return redirect(url_for('staff_trek', trek_id=trek_id))
    
    this_trek.available_slots = request.form.get("available_slots")
    new_status = request.form.get("status")
    this_trek.status = new_status
    db.session.commit()

    # when a trek is marked Completed, close out every booking on it and
    # write a trek_history record for each - this is what user_history.html reads
    if new_status == "Completed":
      for b in this_trek.bookings:
        if b.booking_status == "Booked":
          b.booking_status = "Completed"
          if not b.trek_history:
            th = trek_history(booking_id=b.booking_id, final_status="Completed", remarks="Trek completed successfully")
            db.session.add(th)
      db.session.commit()

    return redirect(url_for('staff_trek', trek_id=trek_id))

  return render_template("staff_trek.html", this_trek=this_trek)


@app.route("/staff/profile", methods=["GET","POST"])
def edit_staff():
  if session.get('role') != 'Staff':
    return redirect(url_for('signin'))
  my_profile = staff_profile.query.filter_by(user_id=session['uid']).first()

  if request.method == "POST":
    my_profile.dino_speciality = request.form.get("dino_speciality")
    my_profile.experience_years = request.form.get("experience_years")
    my_profile.contact = request.form.get("contact")
    db.session.commit()
    return redirect(url_for('staff_dashboard'))

  return render_template("edit_staff.html", my_profile=my_profile)


# ================= USER (TREKKER) =================

@app.route("/user/")
def user_dashboard():
  if session.get('role') != 'Trekker':
    return redirect(url_for('signin'))

  my_profile = trekker.query.filter_by(user_id=session['uid']).first()

  # search/filter treks based on difficulty and location - was missing before
  difficulty = request.args.get('difficulty', '')
  location = request.args.get('location', '')

  q = trek.query.filter_by(status="Open")
  if difficulty:
    q = q.filter_by(difficulty=difficulty)
  if location:
    q = q.filter(trek.location.contains(location))
  available_treks = q.all()

  if my_profile and my_profile.preferred_difficulty and not difficulty:
    preferred = my_profile.preferred_difficulty
    available_treks.sort(key=lambda t: 0 if t.difficulty == preferred else 1)

  my_bookings = my_profile.bookings if my_profile else []
  return render_template("user_dashboard.html", available_treks=available_treks, my_bookings=my_bookings,
                          difficulty=difficulty, location=location)


# Booking

@app.route("/user/trek/<int:trek_id>", methods=["GET","POST"])
def trek_details(trek_id):
  if session.get('role') != 'Trekker':
    return redirect(url_for('signin'))
  this_trek = trek.query.get(trek_id)
  my_profile = trekker.query.filter_by(user_id=session['uid']).first()

  aldready_booked = booking.query.filter_by(trekker_id=my_profile.trekker_id , trek_id=trek_id , booking_status="Booked").first();

  if request.method == "POST":
    # prevent booking a trek that is not Open, or has no slots left
    if this_trek.status != "Open" or this_trek.available_slots <= 0:
      return render_template("trek_details.html", this_trek=this_trek, error_msg="This trek is closed or full")

    # prevent the same trekker booking the same trek twice
    existing = booking.query.filter_by(trekker_id=my_profile.trekker_id, trek_id=trek_id, booking_status="Booked").first()
    if existing:
      return render_template("trek_details.html", this_trek=this_trek, error_msg="You have already booked this trek")

    new_booking = booking(trekker_id=my_profile.trekker_id, trek_id=trek_id , payment_status="Paid")
    this_trek.available_slots = this_trek.available_slots - 1
    db.session.add(new_booking)
    db.session.commit()
    return redirect(url_for('my_bookings'))

  return render_template("trek_details.html", this_trek=this_trek)


@app.route("/user/profile", methods=["GET","POST"])
def edit_trekker():
  if session.get('role') != 'Trekker':
    return redirect(url_for('signin'))
  my_profile = trekker.query.filter_by(user_id=session['uid']).first()

  if request.method == "POST":
    my_profile.address = request.form.get("address")
    my_profile.emergency_contact = request.form.get("emergency_contact")
    my_profile.preferred_difficulty = request.form.get("preferred_difficulty")
    db.session.commit()
    return redirect(url_for('user_dashboard'))

  return render_template("edit_trekker.html", my_profile=my_profile)


@app.route("/user/bookings")
def my_bookings():
  if session.get('role') != 'Trekker':
    return redirect(url_for('signin'))
  my_profile = trekker.query.filter_by(user_id=session['uid']).first()
  bookings_list = my_profile.bookings if my_profile else []
  return render_template("my_bookings.html", bookings_list=bookings_list)

# Trek Cancelling
@app.route("/user/cancel_booking/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):
  if session.get('role')!= 'Trekker':
    return redirect(url_for('signin'))
  my_profile =  trekker.query.filter_by(user_id=session['uid']).first()
  this_booking = booking.query.get(booking_id)

  if this_booking and my_profile and this_booking.trekker_id == my_profile.trekker_id and this_booking.booking_status == "Booked":
    this_booking.booking_status = "Cancelled"
    this_booking.trek.available_slots += 1
    db.session.commit()
  return redirect(url_for('my_bookings'))

@app.route("/user/history")
def user_history():
  if session.get('role') != 'Trekker':
    return redirect(url_for('signin'))
  my_profile = trekker.query.filter_by(user_id=session['uid']).first()
  history_list = []
  if my_profile:
    for b in my_profile.bookings:
      if b.trek_history:
        history_list.append(b)
  return render_template("user_history.html", history_list=history_list)
