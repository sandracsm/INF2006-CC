from flask import Flask
from config import Config
from flask_session import Session
from models.database import db
from routes.auth import auth_bp
from routes.home import home_bp
from routes.project import project_bp
from routes.task import task_bp
from routes.admin_auth import admin_bp
from routes.admin_home import admin_home_bp
from routes.errors import errors_bp  # ✅ Import errors blueprint

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
Session(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(project_bp)
app.register_blueprint(task_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(admin_home_bp)
app.register_blueprint(errors_bp)  # ✅ Register the error handler blueprint

@app.route("/health")
def health_check():
    return "OK", 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
