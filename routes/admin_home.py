import random
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import db
from models.user import User
from models.project import Project
from utils.authentication_helper import admin_required

admin_home_bp = Blueprint("admin_home", __name__)


# Admin Home Route (Only accessible by logged-in admins)
# @admin_home_bp.route("/admin_home")
# @admin_required
# def admin_home():
#     return render_template("admin_home.html")

# Admin Home - User Management Page
@admin_home_bp.route("/admin_home")
@admin_required
def admin_home():
    users = User.query.all()  # Fetch all users

    # Print users in the terminal
    print("\n=== User List ===")
    for user in users:
        print(f"ID: {user.UserID}, Name: {user.Name}, Email: {user.Email}, Disabled: {user.Disabled}")
    print("=================\n")

    return render_template("admin_home.html", users=users)

# Admin Disable/Enable User
@admin_home_bp.route("/disable_user/<int:user_id>", methods=["POST"])
@admin_required
def disable_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        print(f"[ERROR] User with ID {user_id} not found.")  # ✅ Log error to console
        return redirect(url_for("admin_home.admin_home"))

    print(f"\n[LOG] Processing disable request for User ID {user.UserID} - {user.Name}")

    # Fetch all projects where this user is the project owner
    owned_projects = Project.query.filter_by(ProjectOwner=user_id).all()

    for project in owned_projects:
        project_members = project.ProjectMembers.split(",") if project.ProjectMembers else []
        project_members = [uid for uid in project_members if uid != str(user_id)]  # Remove the current owner

        if len(project_members) > 0:
            # Select a random new owner from remaining members
            new_owner_id = random.choice(project_members)
            project.ProjectOwner = int(new_owner_id)
            print(f"[LOG] Ownership of project '{project.ProjectName}' (ID: {project.ProjectID}) transferred from {user.UserID} to {new_owner_id}.")
            flash(f"Ownership of project '{project.ProjectName}' transferred to user {new_owner_id}.", "info")
        else:
            # If the owner is the only member, keep them as owner
            print(f"[LOG] User {user.Name} (ID: {user.UserID}) is the only member of project '{project.ProjectName}' and remains the owner.")
            flash(f"User {user.Name} is the only member of project '{project.ProjectName}' and remains the owner.", "warning")

    # Toggle user status only if ownership is handled
    user.Disabled = not user.Disabled
    db.session.commit()

    status = "disabled" if user.Disabled else "enabled"
    print(f"[LOG] User {user.Name} (ID: {user.UserID}) has been {status}.")
    flash(f"User {user.Name} has been {status}.", "success")

    return redirect(url_for("admin_home.admin_home"))