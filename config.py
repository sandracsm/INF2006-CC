from dotenv import load_dotenv
import os

load_dotenv()  # This loads environment variables from a .env file

class Config:
    SECRET_KEY = "inf2006"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:admin@localhost/task_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = "filesystem"  # Store session data in local files
    SESSION_PERMANENT = False  # Session will expire when the browser closes
    SESSION_USE_SIGNER = True  # Prevents tampering


