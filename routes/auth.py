from flask import Blueprint, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from models.database import db
from models.user import User
from flask_bcrypt import Bcrypt
import re
from utils.authentication_helper import user_required, is_user_logged_in  # ✅ Import helper functions

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if is_user_logged_in():  
        flash("You are already logged in.", "info")
        return redirect(url_for("home.home"))

    # ✅ Clear flash messages when loading login page
    if request.method == "GET":
        get_flashed_messages()

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(Email=email).first()

        if user:
            if user.Disabled:
                flash("Your account has been disabled. Contact an admin.", "danger")
                return redirect(url_for("auth.login"))

            if bcrypt.check_password_hash(user.Password, password):
                session.clear()  # Remove any existing admin session
                session["user_id"] = user.UserID  
                session["user_name"] = user.Name  
                flash("Login successful!", "success")
                return redirect(url_for("home.home"))
            else:
                flash("Incorrect password.", "danger")  # ✅ New error message for incorrect password
        else:
            flash("Invalid email or password.", "danger")  # ✅ Keeps the same message for security reasons

    return render_template("login.html")

@auth_bp.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    password = request.form["password"]
    name = request.form["name"]

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash("Invalid email format.", "danger")
        return redirect(url_for("auth.login"))

    if len(password) < 6:
        flash("Password must be at least 6 characters.", "danger")
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