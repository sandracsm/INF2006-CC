from flask import Blueprint, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from models.database import db
from models.user import User
from utils.authentication_helper import user_required

profile_bp = Blueprint("profile", __name__)

# View & Update Profile
@profile_bp.route("/profile", methods=["GET", "POST"])
@user_required
def profile():
    # ✅ Clear flash messages before adding new ones
    get_flashed_messages()

    user_id = session.get("user_id")
    user = User.query.get(user_id)

    if request.method == "POST":
        new_name = request.form.get("name")
        new_email = request.form.get("email")

        # Check if the email is already taken by another user
        existing_user = User.query.filter(User.Email == new_email, User.UserID != user_id).first()
        if existing_user:
            flash("This email is already registered to another account.", "danger")
        else:
            user.Name = new_name
            user.Email = new_email
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for("profile.profile"))

    return render_template("profile.html", user=user)
