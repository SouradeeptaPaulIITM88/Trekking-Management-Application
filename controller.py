from flask import current_app as  app
from flask import render_template

@app.route("/")
def home():
 return  "hello HMS!"
 

@app.route("/login/")
def signin():
  return render_template("login.html")

app_dict = [
  {"uname" : "abc" , "sname" : "xyz" , "vname" : "Indominous"},
  {"uname" : "def" , "sname" : "uvw" , "vname" : "Velociraptor"},
  {"uname" : "ghi" , "sname" : "pqr" , "vname" : "T.Rex"}
]
@app.route("/admin/")
def admin_console():
  return render_template("admin_dashboard.html", app_data=app_dict)
