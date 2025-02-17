from models.database import db

class Project(db.Model):
    __tablename__ = "projects"
    ProjectID = db.Column(db.Integer, primary_key=True)
    ProjectOwner = db.Column(db.Integer, db.ForeignKey("users.UserID"), nullable=False)
    ProjectMembers = db.Column(db.String(255), nullable=True)
    ProjectName = db.Column(db.String(255), nullable=False)  # Added Project Name
