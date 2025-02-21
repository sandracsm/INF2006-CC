from models.admin import Admin  # Add this line
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from utils.authentication_helper import admin_required, is_admin_logged_in
from flask_bcrypt import Bcrypt

admin_bp = Blueprint("admin", __name__)
bcrypt = Bcrypt()

@admin_bp.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if is_admin_logged_in():  
        flash("You are already logged in as an admin.", "info")
        return redirect(url_for("admin_home.admin_home"))

    # ✅ Clear flash messages before adding new ones
    get_flashed_messages()

    error = None  # Store error messages

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        admin = Admin.query.filter_by(Email=email).first()

        if admin:
            if bcrypt.check_password_hash(admin.Password, password):
                session.clear()  # Remove any existing normal user session
                session["admin_id"] = admin.AdminID  
                session["admin_name"] = admin.Name
                flash("Admin login successful!", "success")
                return redirect(url_for("admin_home.admin_home"))
            else:
                flash("Incorrect password.", "danger")  # ✅ Clear and show new message
        else:
            flash("Invalid email or password.", "danger")  # ✅ Clear and show new message

    return render_template("admin_login.html", error=error)  # ✅ Pass error to template

# Admin Logout Route
@admin_bp.route("/admin_logout")
def admin_logout():
    # ✅ Clear flash messages before adding new ones
    get_flashed_messages()

    session.pop("admin_id", None)
    session.pop("admin_name", None)
    flash("Admin logged out successfully.", "info")
    return redirect(url_for("admin.admin_login"))
