from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, get_flashed_messages
from models.database import db
from models.task import Task
from models.project import Project
from models.user import User
from datetime import datetime

task_bp = Blueprint("task", __name__)

# View Task
@task_bp.route("/tasks")
def view_tasks():
    if "user_id" not in session:
        get_flashed_messages()
        flash("Please log in to continue", "warning")
        return redirect(url_for("auth.login"))

    tasks = Task.query.all()  # Fetch all tasks

    for task in tasks:
        task_owner = User.query.get(task.TaskOwner)  # Get the current task owner
        project = Project.query.get(task.ProjectID)  # Get the associated project

        # ✅ If the task has only one owner and that owner is disabled
        if task_owner and task_owner.Disabled:
            if project:
                task.TaskOwner = project.ProjectOwner  # Assign the project owner as the new task owner
                print(f"[LOG] Task '{task.Title}' (ID: {task.TaskID}) reassigned to project owner {project.ProjectOwner}")
        
        # ✅ Handle multiple members: remove disabled users
        task_members = task.Members.split(",") if task.Members else []
        active_members = [uid for uid in task_members if User.query.get(uid) and not User.query.get(uid).Disabled]

        # ✅ If task had disabled members, update the Members field
        if len(active_members) != len(task_members):  
            task.Members = ",".join(active_members)
            print(f"[LOG] Disabled users removed from Task '{task.Title}' (ID: {task.TaskID})")
        
        # ✅ Commit changes if updates were made
        db.session.commit()

    # ✅ Filter tasks to show only those where the user is the owner or a member
    tasks = Task.query.filter(
        (Task.TaskOwner == session["user_id"]) | (Task.Members.contains(str(session["user_id"])))
    ).all()

    return tasks

# Add Task
@task_bp.route("/tasks/add", methods=["POST"])
def add_task():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    get_flashed_messages()
    title = request.form["title"]
    description = request.form["description"]
    deadline = request.form["deadline"]
    priority = request.form["priority"]
    project_id = request.form["project_id"]
    selected_members = request.form.getlist("members")  # Collect checkboxes

    # Filter out disabled members
    active_members = [
        str(member_id) for member_id in selected_members if not User.query.get(member_id).Disabled
    ]

    # Convert list of active members to a CSV string for storage
    members_str = ",".join(active_members)

    new_task = Task(
        ProjectID=project_id,
        TaskOwner=session["user_id"],
        Members=members_str,
        Title=title,
        Description=description,
        Deadline=deadline,
        Priority=priority,
        Status="Incomplete",
    )

    db.session.add(new_task)
    db.session.commit()

    flash("Task added successfully!", "success")
    return redirect(url_for("home.home"))

# Get Task
@task_bp.route("/tasks/<int:task_id>")
def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({
        "TaskID": task.TaskID,
        "Title": task.Title,
        "Description": task.Description,
        "Deadline": task.Deadline,
        "Priority": task.Priority
    })

@task_bp.route("/tasks/update/<int:task_id>", methods=["POST"])
def update_task(task_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    get_flashed_messages()
    task = Task.query.get(task_id)
    if not task or (task.TaskOwner != session["user_id"] and str(session["user_id"]) not in task.Members.split(",")):
        flash("You do not have permission to edit this task!", "danger")
        return redirect(url_for("home.home"))

    task.Title = request.form["title"]
    task.Description = request.form["description"]
    task.Deadline = request.form["deadline"]
    task.Priority = request.form["priority"]

    db.session.commit()
    flash("Task updated successfully!", "success")
    return redirect(url_for("home.home"))

# Update Task Status
from datetime import datetime

@task_bp.route("/tasks/update_status/<int:task_id>", methods=["POST"])
def update_task_status(task_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    get_flashed_messages()
    task = Task.query.get(task_id)
    if not task or (task.TaskOwner != session["user_id"] and str(session["user_id"]) not in task.Members.split(",")):
        return jsonify({"error": "You do not have permission to update this task!"}), 403

    data = request.get_json()
    new_status = data["status"]

    # ✅ Ensure `task.Deadline` is a datetime object
    task_deadline = task.Deadline
    if isinstance(task_deadline, str):  
        task_deadline = datetime.strptime(task_deadline, "%Y-%m-%d %H:%M:%S")  

    current_date = datetime.now()

    # ✅ Compare datetime objects correctly
    if task_deadline and task_deadline < current_date:
        task.Status = "Overdue"
        if new_status != "Completed":
            return jsonify({"error": "Overdue tasks can only be marked as Completed!"}), 403
    else:
        task.Status = new_status

    db.session.commit()
    return jsonify({"success": True, "message": "Task status updated successfully!"})

# Delete Task
@task_bp.route("/tasks/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    get_flashed_messages()
    task = Task.query.get(task_id)
    if not task or task.TaskOwner != session["user_id"]:
        flash("You do not have permission to delete this task!", "danger")
        return redirect(url_for("home.home"))

    db.session.delete(task)
    db.session.commit()
    flash("Task deleted successfully!", "success")
    return redirect(url_for("home.home"))

# Update Task Owner
@task_bp.route("/tasks/change_owner/<int:task_id>", methods=["POST"])
def change_task_owner(task_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    get_flashed_messages()
    task = Task.query.get(task_id)
    if not task or task.TaskOwner != session["user_id"]:
        flash("You do not have permission to transfer this task!", "danger")
        return redirect(url_for("home.home"))

    new_owner_id = request.form["new_owner_id"]
    new_owner = User.query.get(new_owner_id)

    if not new_owner:
        flash("New owner not found!", "danger")
        return redirect(url_for("home.home"))

    task.TaskOwner = new_owner_id
    db.session.commit()
    
    flash(f"Task '{task.Title}' ownership transferred to {new_owner.Name}.", "success")
    return redirect(url_for("home.home"))
