from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = "filesystem"  # Store session data in local files
    SESSION_PERMANENT = False  # Session will expire when the browser closes
    SESSION_USE_SIGNER = True  # Prevents tampering
