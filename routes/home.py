from flask import Blueprint, render_template, session, redirect, url_for, flash
from models.database import db
from models.project import Project
from models.task import Task
from models.user import User

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    if "user_id" not in session:
        flash("Please log in to continue", "warning")
        return redirect(url_for("auth.login"))

    user_id = str(session["user_id"])

    # Fetch projects where the user is an owner or a member
    user_projects = Project.query.filter(
        (Project.ProjectOwner == session["user_id"]) | (Project.ProjectMembers.like(f"%{user_id}%"))
    ).all()

    user_tasks = Task.query.filter(
        (Task.TaskOwner == session["user_id"]) | (Task.Members.like(f"%{user_id}%"))
    ).all()

    # Fetch project details for tasks
    projects_dict = {str(project.ProjectID): project.ProjectName for project in user_projects}

    # Fetch all users to create a dictionary {UserID: User}
    users = User.query.all()
    users_dict = {str(user.UserID): user for user in users}

    return render_template("home.html", projects=user_projects, tasks=user_tasks, users_dict=users_dict, projects_dict=projects_dict)






