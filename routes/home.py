from flask import Blueprint, render_template, session, redirect, url_for, flash, get_flashed_messages
from models.database import db
from models.project import Project
from models.task import Task
from models.user import User
from utils.authentication_helper import user_required  # Import helper function
from routes.task import view_tasks  # ✅ Import the function

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
@user_required  # Restrict access to logged-in users only
def home():
    # ✅ Clear flash messages before adding new ones
    get_flashed_messages()

    user_id = str(session["user_id"])

    # Fetch projects where the user is an owner or a member
    user_projects = Project.query.filter(
        (Project.ProjectOwner == session["user_id"]) | (Project.ProjectMembers.like(f"%{user_id}%"))
    ).all()

    user_tasks = view_tasks()

    # Fetch project details for tasks
    projects_dict = {str(project.ProjectID): project.ProjectName for project in user_projects}

    # Fetch all users to create a dictionary {UserID: User}
    users = User.query.filter_by(Disabled=False).all()
    users_dict = {str(user.UserID): user for user in users}

    # Task analytics calculations
    total_tasks = len(user_tasks)
    completed_tasks = sum(1 for task in user_tasks if task.Status == "Completed")
    pending_tasks = total_tasks - completed_tasks

    # Task distribution by priority
    priority_counts = {"Low": 0, "Medium": 0, "High": 0}
    for task in user_tasks:
        if task.Priority in priority_counts:
            priority_counts[task.Priority] += 1

    # Task distribution by status
    status_counts = {"Incomplete": 0, "In Progress": 0, "Completed": 0, "Overdue": 0}
    for task in user_tasks:
        if task.Status in status_counts:
            status_counts[task.Status] += 1

    return render_template("home.html", 
                            projects=user_projects, 
                            tasks=user_tasks,
                            users_dict=users_dict,
                            projects_dict=projects_dict,
                            total_tasks=total_tasks,
                            completed_tasks=completed_tasks,
                            pending_tasks=pending_tasks,
                            priority_counts=priority_counts,
                            status_counts=status_counts,)
