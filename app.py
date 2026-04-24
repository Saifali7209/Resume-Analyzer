from flask import Flask, render_template, request, redirect, session
from db import Base, engine, sessionlocal
from ai import analyze_resume
import models
import PyPDF2
import json

app = Flask(__name__)
app.secret_key = "secret123"

Base.metadata.create_all(bind=engine)

# HOME
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

# SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    db = sessionlocal()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        existing_user = db.query(models.User).filter_by(email=email).first()
        if existing_user:
            return "user already exist"
        user = models.User(email=email, password=password)
        db.add(user)
        db.commit()
        return redirect("/login")
    return render_template("signup.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    db = sessionlocal()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = db.query(models.User).filter_by(email=email, password=password).first()
        if user:
            session["user"] = user.email
            return redirect("/dashboard")
        else:
            return "Invalid credentials"
    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    result = None
    if request.method == "POST":
        resume_text = request.form.get("resume_text")
        resume_file = request.files.get("resume_file")
        
        # PDF Parsing
        if resume_file and resume_file.filename.endswith('.pdf'):
            reader = PyPDF2.PdfReader(resume_file)
            resume_text = ""
            for page in reader.pages:
                resume_text += page.extract_text()
        
        user_goal = request.form.get("user_goal")
        if resume_text:
            result = analyze_resume(resume_text, user_goal)
            
    return render_template("dashboard.html", result=result)

# HISTORY
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")
    
    db = sessionlocal()
    user = db.query(models.User).filter_by(email=session["user"]).first()
    reports = db.query(models.Reports).filter_by(user_id=user.id).all()

    parsed_reports = []
    for r in reports:
        try:
            parsed_result = json.loads(r.result)
        except:
            parsed_result = {} # Empty dict if json invalid
            
        parsed_reports.append({
            "resume": r.resume_text,
            "result": parsed_result
        })
    
    return render_template("history.html", reports=parsed_reports)

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)