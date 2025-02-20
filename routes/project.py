from flask import Blueprint, jsonify, request, redirect, url_for, session, flash, render_template
from models.database import db
from models.project import Project
from models.user import User
from models.task import Task


project_bp = Blueprint("project", __name__)

# View Projects
@project_bp.route("/projects")
def view_projects():
    if "user_id" not in session:
        flash("Please log in to continue", "warning")
        return redirect(url_for("auth.login"))

    projects = Project.query.filter_by(ProjectOwner=session["user_id"]).all()
    return render_template("home.html", projects=projects)

# Add Project
@project_bp.route("/projects/add", methods=["POST"])
def add_project():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    project_name = request.form["name"]
    new_project = Project(ProjectOwner=session["user_id"], ProjectMembers=str(session["user_id"]), ProjectName=project_name)
    
    db.session.add(new_project)
    db.session.commit()
    
    flash("Project added successfully!", "success")
    return redirect(url_for("home.home"))

@project_bp.route("/projects/<int:project_id>/members/json")
def get_project_members_json(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    member_ids = project.ProjectMembers.split(",")
    
    # Fetch only **active users** (not disabled)
    members = User.query.filter(User.UserID.in_(member_ids), User.Disabled == False).all()

    return jsonify({"members": [{"UserID": member.UserID, "Name": member.Name} for member in members]})

# Update Project
@project_bp.route("/projects/update/<int:project_id>", methods=["POST"])
def update_project(project_id):
    if "user_id" not in session:
        flash("Unauthorized", "danger")
        return redirect(url_for("home.home"))

    project = Project.query.get(project_id)
    if not project or project.ProjectOwner != session["user_id"]:
        flash("You do not have permission to edit this project!", "danger")
        return redirect(url_for("home.home"))

    project.ProjectName = request.form["name"]
    
    delete_task_ids = request.form.getlist("delete_tasks")
    if delete_task_ids:
        Task.query.filter(Task.TaskID.in_(delete_task_ids)).delete(synchronize_session=False)
    
    db.session.commit()
    flash("Project updated successfully!", "success")
    return redirect(url_for("home.home"))

# Delete Project
@project_bp.route("/projects/delete/<int:project_id>", methods=["POST"])
def delete_project(project_id):
    if "user_id" not in session:
        flash("Unauthorized", "danger")
        return redirect(url_for("home.home"))

    project = Project.query.get(project_id)
    if not project or project.ProjectOwner != session["user_id"]:
        flash("You do not have permission to delete this project!", "danger")
        return redirect(url_for("home.home"))

    Task.query.filter_by(ProjectID=project_id).delete()  # Delete all tasks
    db.session.delete(project)
    db.session.commit()
    
    flash("Project deleted successfully!", "success")
    return redirect(url_for("home.home"))

# Get Project
@project_bp.route("/projects/<int:project_id>")
def get_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    tasks = Task.query.filter_by(ProjectID=project_id).all()
    
    return jsonify({
        "ProjectID": project.ProjectID,
        "ProjectName": project.ProjectName,
        "tasks": [{"TaskID": task.TaskID, "Title": task.Title} for task in tasks]
    })


# View Members
@project_bp.route("/projects/<int:project_id>/members")
def manage_members(project_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    project = Project.query.get(project_id)
    if not project or project.ProjectOwner != session["user_id"]:
        flash("You do not have permission to manage this project!", "danger")
        return redirect(url_for("home.home"))

    member_ids = project.ProjectMembers.split(",") if project.ProjectMembers else []
    members = User.query.filter(User.UserID.in_(member_ids)).all()
    
    return render_template("manage_members.html", project=project, members=members)

# Add Member
@project_bp.route("/projects/<int:project_id>/add_member", methods=["POST"])
def add_member(project_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    project = Project.query.get(project_id)
    if not project or project.ProjectOwner != session["user_id"]:
        flash("You do not have permission to manage this project!", "danger")
        return redirect(url_for("home.home"))

    user_email = request.form["email"]
    new_member = User.query.filter_by(Email=user_email).first()

    if not new_member:
        flash("User not found!", "danger")
        return redirect(url_for("project.manage_members", project_id=project_id))

    if new_member.Disabled:
        flash("This user is disabled and cannot be added to the project.", "danger")  # ✅ New check for disabled user
        return redirect(url_for("project.manage_members", project_id=project_id))

    if str(new_member.UserID) in project.ProjectMembers.split(","):
        flash("User is already a member!", "warning")
        return redirect(url_for("project.manage_members", project_id=project_id))

    project.ProjectMembers += f",{new_member.UserID}"
    db.session.commit()
    
    flash("Member added successfully!", "success")
    return redirect(url_for("project.manage_members", project_id=project_id))

# Remove Member
@project_bp.route("/projects/<int:project_id>/remove_member/<int:user_id>", methods=["POST"])
def remove_member(project_id, user_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    project = Project.query.get(project_id)
    if not project or project.ProjectOwner != session["user_id"]:
        flash("You do not have permission to manage this project!", "danger")
        return redirect(url_for("home.home"))

    member_ids = project.ProjectMembers.split(",")
    if str(user_id) not in member_ids:
        flash("User is not in this project!", "danger")
        return redirect(url_for("project.manage_members", project_id=project_id))

    member_ids.remove(str(user_id))
    project.ProjectMembers = ",".join(member_ids)
    db.session.commit()
    
    flash("Member removed successfully!", "success")
    return redirect(url_for("project.manage_members", project_id=project_id))
