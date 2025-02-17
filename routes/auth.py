from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import db
from models.user import User
from flask_bcrypt import Bcrypt
import re

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(Email=request.form["email"]).first()
        if user and bcrypt.check_password_hash(user.Password, request.form["password"]):
            session["user_id"] = user.UserID  # Store user ID in session
            session["user_name"] = user.Name  # Store user name in session
            flash("Login successful!", "success")
            return redirect(url_for("home.home"))
        else:
            flash("Invalid email or password", "danger")
    return render_template("login.html")

@auth_bp.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    password = request.form["password"]
    name = request.form["name"]

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash("Invalid email format", "danger")
        return redirect(url_for("auth.login"))

    if len(password) < 6:
        flash("Password must be at least 6 characters", "danger")
        return redirect(url_for("auth.login"))

    hashed_password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
    new_user = User(Name=name, Email=email, Password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    flash("Registration successful!", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route("/logout")
def logout():
    session.clear()  # Clear session data
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
