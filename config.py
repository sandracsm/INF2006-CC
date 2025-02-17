from dotenv import load_dotenv
import os

load_dotenv()  # This loads environment variables from a .env file

# SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:Pa55w0rdYOU5uck@localhost/task_db" # LOCAL

class Config:
    SECRET_KEY = "inf2006"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:Pa55w0rdYOU5uck@database-1.cxsztknjejlo.us-east-1.rds.amazonaws.com/task_db" # LOCAL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = "filesystem"  # Store session data in local files
    SESSION_PERMANENT = False  # Session will expire when the browser closes
    SESSION_USE_SIGNER = True  # Prevents tampering


