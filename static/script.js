function showTab(tab) {
    // Hide both forms initially
    document.getElementById('login-form').style.display = tab === 'login' ? 'block' : 'none';
    document.getElementById('register-form').style.display = tab === 'register' ? 'block' : 'none';

    // Remove the 'active-tab' class from all buttons
    const buttons = document.querySelectorAll('.tabs button');
    buttons.forEach(button => button.classList.remove('active-tab'));

    // Add the 'active-tab' class to the clicked tab
    if (tab === 'login') {
        document.querySelector('.tabs button:nth-child(1)').classList.add('active-tab'); // Login button active
    } else if (tab === 'register') {
        document.querySelector('.tabs button:nth-child(2)').classList.add('active-tab'); // Register button active
    }
}

// Default to "Login" tab
document.addEventListener('DOMContentLoaded', () => {
    showTab('login');
});

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".status-dropdown").forEach(select => {
        updateDropdownColor(select);  // Apply color on page load
    });
});

function updateDropdownColor(selectElement) {
    let status = selectElement.value.toLowerCase().replace(" ", "-");
    selectElement.classList.remove("incomplete", "in-progress", "completed", "overdue");
    selectElement.classList.add(status);
}

function validateLogin() {
    let email = document.querySelector('input[name="email"]').value;
    let password = document.querySelector('input[name="password"]').value;

    if (!email.includes('@')) {
        alert("Invalid email address");
        return false;
    }
    if (password.length < 6) {
        alert("Password must be at least 6 characters");
        return false;
    }
    return true;
}

function showAddProjectModal() {
    // Display the modal overlay
    document.getElementById('addProjectModal').style.display = 'flex';
    // Disable scrolling in the background
    document.body.classList.add('modal-open');
}

function showEditProjectModal(projectId) {
    // Display the modal overlay
    document.getElementById('editProjectModal').style.display = 'flex';
    // Disable scrolling in the background
    document.body.classList.add('modal-open');
    fetch(`/projects/${projectId}`)
        .then(response => response.json())
        .then(project => {
            document.getElementById("editProjectId").value = project.ProjectID;
            document.getElementById("editProjectName").value = project.ProjectName;
            document.getElementById("editProjectForm").action = `/projects/update/${project.ProjectID}`;
            
            let container = document.getElementById("projectTasksContainer");
            container.innerHTML = "";
            project.tasks.forEach(task => {
                let label = document.createElement("label");
                let checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.name = "delete_tasks";
                checkbox.value = task.TaskID;
                label.appendChild(checkbox);
                label.appendChild(document.createTextNode(" " + task.Title));
                container.appendChild(label);
                container.appendChild(document.createElement("br"));
            });

        })
        .catch(error => console.error("Error loading project:", error));
}

function validateProject() {
    let name = document.querySelector('input[name="name"]').value.trim();
    if (name === "") {
        alert("Project Name is required");
        return false;
    }
    return true;
}

function showAddTaskModal(projectId) {
    // Display the modal overlay
    document.getElementById('addTaskModal').style.display = 'flex';
    // Disable scrolling in the background
    document.body.classList.add('modal-open');
    // Optionally, set the project ID in the task modal dynamically
    document.querySelector('#addTaskModal select[name="project_id"]').value = projectId;
    let projectDropdown = document.getElementById("projectDropdown");
    if (projectDropdown.value) {
        loadProjectMembers(projectDropdown.value);
    }
}

function validateTask() {
    let title = document.querySelector('input[name="title"]').value.trim();
    let project = document.getElementById("projectDropdown").value;
    let members = document.querySelectorAll('input[name="members"]:checked');

    if (title === "") {
        alert("Task title is required");
        return false;
    }
    if (project === "") {
        alert("Please select a project");
        return false;
    }
    if (members.length === 0) {
        alert("Please select at least one member");
        return false;
    }
    return true;
}

function showEditTaskModal(taskId) {
    document.getElementById('editTaskModal').style.display = 'flex';
    document.body.classList.add('modal-open');
    fetch(`/tasks/${taskId}`)
        .then(response => response.json())
        .then(task => {
            document.getElementById("editTaskId").value = task.TaskID;
            document.getElementById("editTaskTitle").value = task.Title;
            document.getElementById("editTaskDescription").value = task.Description;
        // Convert deadline to the correct format for <input type="datetime-local">
        if (task.Deadline) {
            let deadline = new Date(task.Deadline);
            let formattedDeadline = deadline.toISOString().slice(0, 16);
            document.getElementById("editTaskDeadline").value = formattedDeadline;
        }
            document.getElementById("editTaskPriority").value = task.Priority;
            document.getElementById("editTaskForm").action = `/tasks/update/${task.TaskID}`;
        })
        .catch(error => console.error("Error loading task:", error));
}

function updateTaskStatus(selectElement) {
    let taskId = selectElement.getAttribute("data-task-id");
    let newStatus = selectElement.value;

    fetch(`/tasks/update_status/${taskId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Task status updated!");
            
            // ✅ Remove previous class and apply new class for background color
            selectElement.classList.remove("incomplete", "in-progress", "completed", "overdue");
            selectElement.classList.add(newStatus.toLowerCase().replace(" ", "-")); 
        } else {
            alert("Failed to update task status.");
        }
    })
    .catch(error => console.error("Error updating task status:", error));
}


// Restrict deadline selection to today onwards
function setMinDeadline() {
    let today = new Date().toISOString().split("T")[0] + "T00:00";
    document.querySelectorAll('input[type="datetime-local"]').forEach(input => {
        input.setAttribute("min", today);
    });
}

// Run this function when the page loads
document.addEventListener("DOMContentLoaded", setMinDeadline);


function loadProjectMembers(projectId) {
    let container = document.getElementById("memberCheckboxContainer");
    container.innerHTML = ""; // Clear previous checkboxes

    if (!projectId) return;

    fetch(`/projects/${projectId}/members/json`)
        .then(response => response.json())
        .then(data => {
            data.members.forEach(member => {
                let label = document.createElement("label");
                let checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.name = "members";
                checkbox.value = member.UserID;
                label.appendChild(checkbox);
                label.appendChild(document.createTextNode(" " + member.Name));
                container.appendChild(label);
                container.appendChild(document.createElement("br"));
            });
        })
        .catch(error => console.error("Error loading members:", error));
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    document.body.classList.remove('modal-open');
}

