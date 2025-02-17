from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.database import db
from models.task import Task
from models.project import Project
from datetime import datetime

task_bp = Blueprint("task", __name__)

# View Tasks
@task_bp.route("/tasks")
def view_tasks():
    if "user_id" not in session:
        flash("Please log in to continue", "warning")
        return redirect(url_for("auth.login"))

    tasks = Task.query.filter_by(TaskOwner=session["user_id"]).all()
    return render_template("home.html", tasks=tasks)

# Add Task
@task_bp.route("/tasks/add", methods=["POST"])
def add_task():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    title = request.form["title"]
    description = request.form["description"]
    deadline = request.form["deadline"]
    priority = request.form["priority"]
    project_id = request.form["project_id"]
    members = request.form.getlist("members")  # Collect checkboxes

    # Convert list of members to a CSV string for storage
    members_str = ",".join(members)

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

#Get Task
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

    task = Task.query.get(task_id)
    if not task or task.TaskOwner != session["user_id"]:
        flash("You do not have permission to delete this task!", "danger")
        return redirect(url_for("home.home"))

    db.session.delete(task)
    db.session.commit()
    flash("Task deleted successfully!", "success")
    return redirect(url_for("home.home"))
