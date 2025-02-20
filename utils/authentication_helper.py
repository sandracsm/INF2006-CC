from functools import wraps
from flask import session, redirect, url_for, flash

# ==========================
#  ADMIN SESSION CHECK
# ==========================

def admin_required(f):
    """Decorator to restrict access to admin-only pages."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_id" not in session:
            flash("Access denied. Admins only.", "danger")
            return redirect(url_for("admin.admin_login"))
        return f(*args, **kwargs)
    return decorated_function


def is_admin_logged_in():
    """Check if an admin is currently logged in."""
    return "admin_id" in session


# ==========================
#  USER SESSION CHECK
# ==========================

def user_required(f):
    """Decorator to restrict access to user-only pages."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Access denied. Please log in.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def is_user_logged_in():
    """Check if a user is currently logged in."""
    return "user_id" in session
