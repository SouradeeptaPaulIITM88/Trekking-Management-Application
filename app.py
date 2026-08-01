from flask import Flask
from models import db, user

app=None

def setup_app():
  global app
  app=Flask(__name__)
  app.secret_key = "trekking-secret-key"   # needed so Flask session works (used to remember who is logged in)
  app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.sqlite3"
  app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
  db.init_app(app)
  app.app_context().push()
  print("Trekking management app setup is done......")
  db.create_all()

  # Admin must pre-exist (no admin registration allowed) - create one if it doesn't exist yet
  if not user.query.filter_by(role="Admin").first():
    admin_user = user(full_name="Admin", email="admin@trekking.com", password="admin123", role="Admin", status="Active")
    db.session.add(admin_user)
    db.session.commit()
    print("Default Admin created -> admin@trekking.com / admin123")

setup_app()

from controller import *
if __name__ == "__main__":
  app.run(debug=True , use_reloader=False)
