from models.database import db

class Task(db.Model):
    __tablename__ = "tasks"
    TaskID = db.Column(db.Integer, primary_key=True)
    ProjectID = db.Column(db.Integer, db.ForeignKey("projects.ProjectID"), nullable=False)
    TaskOwner = db.Column(db.Integer, db.ForeignKey("users.UserID"), nullable=False)
    Members = db.Column(db.String(255), nullable=True)
    Title = db.Column(db.String(255), nullable=False)
    Description = db.Column(db.Text, nullable=True)
    Deadline = db.Column(db.String(255), nullable=True)
    Priority = db.Column(db.Enum("Low", "Medium", "High"), default="Low")
    Status = db.Column(db.Enum("Incomplete", "In Progress", "Completed", "Overdue"), default="Incomplete")
