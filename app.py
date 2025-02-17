from flask import Flask, session
from config import Config
from flask_session import Session
from models.database import db
from routes.auth import auth_bp
from routes.home import home_bp
from routes.project import project_bp
from routes.task import task_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
Session(app)  # Initialize session handling

# Clear session on app start (app restart behavior)
@app.before_request
def clear_session_on_restart():
    if not session:  # Only clear if session exists, prevents clearing after user login
        session.clear()

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(project_bp)
app.register_blueprint(task_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
