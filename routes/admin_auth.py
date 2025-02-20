from models.admin import Admin  # Add this line
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.authentication_helper import admin_required, is_admin_logged_in
from flask_bcrypt import Bcrypt

admin_bp = Blueprint("admin", __name__)
bcrypt = Bcrypt()

@admin_bp.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if is_admin_logged_in():  
        flash("You are already logged in as an admin.", "info")
        return redirect(url_for("admin_home.admin_home"))

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
                error = "Incorrect password."  # ✅ Show error if password is wrong
        else:
            error = "Invalid email or password."  # ✅ Show error if admin doesn't exist

    return render_template("admin_login.html", error=error)  # ✅ Pass error to template

# Admin Logout Route
@admin_bp.route("/admin_logout")
def admin_logout():
    session.pop("admin_id", None)
    session.pop("admin_name", None)
    flash("Admin logged out successfully.", "info")
    return redirect(url_for("admin.admin_login"))
